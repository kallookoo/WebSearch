import sublime
import sublime_plugin
import os
import json
import re
import webbrowser
try:
    # Python 3
    from urllib.parse import quote_plus as url_text_encode
    from collections import OrderedDict
except ImportError:
    # Python 2
    from urllib import quote_plus as url_text_encode
    from st2.ordereddict import OrderedDict

is_ST2 = False if int(sublime.version()) >= 3000 else True

class WebSearch(object):

    def __init__(self):
        self.settings = sublime.load_settings('WebSearch.sublime-settings')
        self.update()
        self.settings.clear_on_change('WebSearch')
        self.settings.add_on_change('WebSearch', self.update)

    def update(self):
        update_deprecated = False
        if self.settings.has('active'):
            update_deprecated = True
            self.settings.set('current_engine', self.settings.get('active', 'Google'))
        if self.settings.has('engines_for_sources'):
            update_deprecated = True
            self.settings.set('use_developer_engines', self.settings.get('engines_for_sources', False))
        if update_deprecated:
            self.settings.save_settings('WebSearch.sublime-settings')
        self.engines = self.generate_engines_list()
        self.engine = self.normalize_name_engine(self.settings.get('current_engine', 'Google'))
        self.browser_mode = self.settings.get('browser_mode', 'tab')
        self.generate_context_menu(self.settings.get('context_menu_with_children', False))
        self.generate_status_bar()

    def generate_engines_list(self):
        engines = {
            "Ask": "https://www.ask.com/web?q=",
            "Bing": "https://www.bing.com/search?q=",
            "DuckDuckGo": "https://duckduckgo.com/?q=",
            "Google": "https://google.com/search?q=",
            "Wikipedia": "https://wikipedia.org/w/index.php?search=",
            "Yahoo": "https://search.yahoo.com/search?p="
        }
        user_engines = self.settings.get('engines', {})
        if len(user_engines):
            engines.update(user_engines)
        if self.settings.get('use_developer_engines', False):
            developer_engines = {
                "MDN": "https://developer.mozilla.org/search?q=",
                "PHP": "https://php.net/search.php?show=quickref&pattern=",
                "Python": "https://docs.python.org/3/search.html?q=",
                "Python2": "https://docs.python.org/2/search.html?q=",
                "WordPress": "https://developer.wordpress.org/?s="
            }
            user_developer_engines = self.settings.get('developer_engines', {})
            if len(user_developer_engines):
                developer_engines.update(user_developer_engines)
            engines.update(developer_engines)
        exclude_engines = self.settings.get('exclude_engines_from_list', [])
        if len(exclude_engines):
            _engines = {}
            for key in engines:
                exclude = '|'.join([re.escape(k) for k in exclude_engines if len(k.strip())])
                if re.match(r'^(' + exclude + ')$', key, re.IGNORECASE | re.UNICODE) == None:
                    _engines[key] = engines[key]
            engines = _engines
        return OrderedDict(sorted(engines.items(), key=lambda i: i[0].lower()))

    def normalize_name_engine(self, name):
        for key in self.engines:
            if re.match(r'^' + name + '$', key, re.IGNORECASE | re.UNICODE) != None:
                name = key
                break
        return name

    def generate_context_menu(self, is_children):
        data = [{'caption': '-'}, { 'command': 'web_search', 'args': { 'input_panel': False } }, {'caption': '-'}]
        if is_children:
            childrens = []
            for k in self.engines:
                childrens.append({'command': 'web_search', 'args': {'input_panel': False, 'engine': k }})
            if len(childrens):
                data = [{'caption': '-'}, {'caption': 'Web Search', 'children': childrens}, {'caption': '-'}]
        plugin_directory = os.path.join(sublime.packages_path(), 'WebSearch')
        context_menu_file = os.path.join(plugin_directory, 'Context.sublime-menu')
        try:
            with open(context_menu_file, 'r') as file:
                context_menu_data = json.load(file)
        except:
            context_menu_data = []
        if context_menu_data != data:
            if not os.path.isdir(plugin_directory):
                os.makedirs(plugin_directory)
            with open(context_menu_file, 'w') as file:
                json.dump(data, file, indent=4)

    def get_current_engine(self, engine=False):
        if engine:
            if not engine in self.engines:
                engine = self.normalize_name_engine(engine)
        else:
            engine = self.engine
        return engine

    def update_current_engine(self, engine):
        if not engine in self.engines:
            engine = self.normalize_name_engine(engine)
        if engine in self.engines:
            self.settings.set('current_engine', engine)
            self.engine = engine

    def update_status_bar(self, view=None, engine=False):
        if self.settings.get('show_current_engine_on_status_bar', False):
            text = self.settings.get('status_bar_text_prefix', 'WebSearch:').strip()
            engine = self.get_current_engine(engine)
            if len(text):
                view.set_status('WebSearch.engine', '%s %s' % (text, engine))
            else:
                view.set_status('WebSearch.engine', engine)
        else:
            view.erase_status('WebSearch.engine')

    def generate_status_bar(self, view=None):
        if None == view:
            for window in sublime.windows():
                for view in window.views():
                    self.update_status_bar(view)
        else:
            self.update_status_bar(view)

class WebSearchCommands(object):

    current_text = ''

    def get_search_text(self, view):
        if len(self.current_text):
            return self.current_text
        text = []
        for region in view.sel():
            if region.empty():
                # if we have no selection grab the current word
                word = view.word(region)
                if not word.empty():
                    word = view.substr(word).strip()
                    # Only if is alphanumeric
                    if re.search(r'\w+', word) != None:
                        text.append(word)
            else:
                text.append(view.substr(region).strip())
        if len(text):
            return ' '.join(text)
        return ''

    def get_setting(self, key, default=None):
        return WebSearch.settings.get(key, default)

    def search(self, text, url=None):
        if len(text):
            try:
                engine = self.engine
            except:
                engine = False if not 'engine' in self.args else self.args['engine']
            engine = WebSearch.get_current_engine(engine)
            url = '' if not engine in WebSearch.engines else WebSearch.engines[engine]
            if url.startswith('http'):
                url = url + url_text_encode(text)
                if 'tab' == WebSearch.browser_mode:
                    webbrowser.open_new_tab(url)
                else:
                    webbrowser.open_new(url)
        self.current_text = ''

    def on_engine_done(self, index):
        pass

    def show_engine_panel(self):
        self.items = [k for k in WebSearch.engines]
        self.window.show_quick_panel(self.items, self.on_engine_done)

class WebSearchCommand(sublime_plugin.TextCommand,WebSearchCommands):

    def __init__(self, view):
        self.view = view
        self.window = view.window()
        self.update_attributes()
        WebSearch.settings.add_on_change('WebSearch', self.update_attributes)

    def update_attributes(self):
        self.context_menu_with_children = self.get_setting('context_menu_with_children', False)
        self.context_menu_description = int(self.get_setting('context_menu_description', 1))
        self.context_menu_description_length = int(self.get_setting('context_menu_description_length', 10))
        self.engine_change = self.get_setting('engine_change', False)

    def run(self, edit, **args):
        self.args = args
        if not 'input_panel' in self.args:
            self.args['input_panel'] = False
        if self.engine_change and self.args['input_panel']:
            sublime.set_timeout(self.show_engine_panel, 10)
        else:
            self.search(self.get_search_text(self.view))

    def on_engine_done(self, index):
        if index != -1:
            if self.engine_change and self.args['input_panel']:
                self.engine = self.items[index]
            else:
                self.engine = False
            self.search(self.get_search_text(self.view), WebSearch.get_current_engine(self.items[index]))

    def is_enabled(self):
        return True if len(self.get_search_text(self.view)) else False

    def is_visible(self):
        if self.context_menu_with_children:
            return True
        return self.is_enabled()

    def description(self, **args):
        type_caption = self.context_menu_description
        text_caption = "Web Search"
        engine = False if not 'engine' in args else args['engine']
        engine = WebSearch.get_current_engine(engine)
        if self.context_menu_with_children:
            if type_caption == 1:
                type_caption = 2
        if type_caption == 3:
            text = self.get_search_text(self.view)
            length = self.context_menu_description_length + 3
            text = text if not len(text) > length else text[0:length] + '...'
            text_caption = "Search in %s for '%s'" % (engine, text)
            length_caption = len(engine) + 20
            if len(text_caption) > length_caption:
                text_caption = text_caption[0:length_caption] + '...'
        elif type_caption == 2:
            text_caption = "Search in %s" % (engine)
        return text_caption

class WebSearchEnterCommand(sublime_plugin.WindowCommand,WebSearchCommands):

    def run(self, **args):
        self.args = args
        if not 'input_panel' in self.args:
            self.args['input_panel'] = False
        self.engine_change = self.get_setting('engine_change', False)
        if self.engine_change and self.args['input_panel']:
            sublime.set_timeout(self.show_engine_panel, 10)
        else:
            sublime.set_timeout(self.show_search_panel, 10)

    def on_engine_done(self, index):
        if index != -1:
            if self.engine_change and self.args['input_panel']:
                self.engine = self.items[index]
            else:
                self.engine = False
        sublime.set_timeout(self.show_search_panel, 10)

    def show_search_panel(self):
        self.window.show_input_panel('Enter a search text', '', self.on_search_done)

    def on_search_done(self, text):
        text = text.strip()
        if len(text):
            self.search(text)

class WebSearchEngineCommand(sublime_plugin.WindowCommand,WebSearchCommands):

    def run(self, **args):
        self.args = args
        sublime.set_timeout(self.show_engine_panel, 10)

    def on_engine_done(self, index):
        if index != -1:
            WebSearch.update_current_engine(self.items[index])

class WebSearchEventListener(sublime_plugin.EventListener):

    def on_new(self, view):
        WebSearch.update_status_bar(view)

    def on_load(self, view):
        WebSearch.update_status_bar(view)

    def on_clone(self, view):
        WebSearch.update_status_bar(view)

def plugin_loaded():
    global WebSearch
    WebSearch = WebSearch()

if is_ST2:
    WebSearch = WebSearch()        