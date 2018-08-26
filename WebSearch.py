import sublime
import sublime_plugin
import webbrowser
import re
import os
import collections
import json

try:
    # Python 3
    from urllib import quote as url_text_encode
except ImportError:
    # Python 2
    from urllib.parse import quote_plus as url_text_encode


def is_ST2():
    return False if int(sublime.version()) >= 3000 else True

def get_engines():
    s = sublime.load_settings('WebSearch.sublime-settings')
    engines = {
        "Ask": "https://www.ask.com/web?q=",
        "Bing": "https://www.bing.com/search?q=",
        "DuckDuckGo": "https://duckduckgo.com/?q=",
        "Google": "https://google.com/search?q=",
        "Wikipedia": "https://wikipedia.org/w/index.php?search=",
        "Yahoo": "https://search.yahoo.com/search?p="
    }
    user_engines = s.get('engines', {})
    if len(user_engines):
        engines.update(user_engines)
    if s.get('engines_for_sources', s.get('use_developer_engines', False)):
        developer_engines = {
            "MDN": "https://developer.mozilla.org/search?q=",
            "PHP": "https://php.net/search.php?show=quickref&pattern=",
            "Python": "https://docs.python.org/3/search.html?q=",
            "Python2": "https://docs.python.org/2/search.html?q=",
            "WordPress": "https://developer.wordpress.org/?s="
        }
        user_developer_engines = s.get('developer_engines', {})
        if len(user_developer_engines):
            developer_engines.update(user_developer_engines)
        engines.update(developer_engines)
    exclude_engines = s.get('exclude_engines_from_list', [])
    if len(exclude_engines):
        exclude_engines.extend([v.lower() for v in exclude_engines])
        exclude_engines.extend([v.upper() for v in exclude_engines])
        engines = {key: value for key, value in engines.items() if not key in exclude_engines}
    return collections.OrderedDict(sorted(engines.items(), key=lambda i: i[0].lower()))

def get_current_engine(engine=False):
    if not engine:
        s = sublime.load_settings('WebSearch.sublime-settings')
        engine = s.get('active', s.get('current_engine', 'Google'))
    engines = get_engines()
    if not engine in engines:
        for k in engines:
            if engine.lower() == k.lower():
                engine = k
                break
    return engine

def generate_context_menu(children=False):
    plugin_directory = os.path.join(sublime.packages_path(), 'WebSearch')
    context_menu_file = os.path.join(plugin_directory, 'Context.sublime-menu')
    if not os.path.isdir(plugin_directory):
        os.makedirs(plugin_directory)
    if children:
        template = [{'caption': '-'}]
        children_template = []
        for k in get_engines():
            children_template.append({ 'command': 'web_search', 'args': { 'input_panel': False, 'engine': k } })
        template.extend([{'caption': 'WebSearch', 'children': children_template}, {'caption': '-'}])
    else:
        template = [{ "caption": "-" },{ "command": "web_search", "args": { "input_panel": False } },{ "caption": "-" }]
    with open(context_menu_file, 'w') as file:
        json.dump(template, file, indent=4)

def update_status_bar(view=None):
    def status_bar(view, s):
        text = s.get('status_bar_text_prefix', 'WebSearch:').strip()
        engine = get_current_engine()
        if s.get('show_current_engine_on_status_bar', False):
            if len(text):
                view.set_status('WebSearch.engine', '%s %s' % (text, engine))
            else:
                view.set_status('WebSearch.engine', engine)
        else:
            view.erase_status('WebSearch.engine')
    s = sublime.load_settings('WebSearch.sublime-settings')
    if None == view:
        for window in sublime.windows():
            for view in window.views():
                status_bar(view, s)
    else:
        status_bar(view, s)

def update_context_menu():
    context_with_children = sublime.load_settings('WebSearch.sublime-settings').get('context_menu_with_children', False)
    generate_context_menu(context_with_children)
    update_status_bar()

def plugin_loaded():
    update_context_menu()
    s = sublime.load_settings('WebSearch.sublime-settings')
    s.clear_on_change('web_search_reload')
    s.add_on_change('web_search_reload', update_context_menu)

if is_ST2():
    plugin_loaded()

class WebSearchCommon(object):

    def get_text(self, view):
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
        return ' '.join(text).strip()

    def get_setting(self, key, default=None):
        return sublime.load_settings('WebSearch.sublime-settings').get(key, default)

    def set_engine_setting(self, engine):
        settings = sublime.load_settings('WebSearch.sublime-settings')
        settings.set('current_engine', get_current_engine(engine))
        update_status_bar()

    def get_engines(self):
        return get_engines()

    def get_engine(self, name):
        engines = self.get_engines()
        name = get_current_engine(name)
        if name in engines:
            return engines[name]
        return ''

    def search(self, text, url=None):
        engine_name = self.get_setting('active', self.get_setting('current_engine', 'Google'))
        url = self.get_engine(engine_name)
        if url.startswith('http') and len(text):
            self.webbrowser(url + url_text_encode(text))

    def webbrowser(self, url):
        mode = self.get_setting('browser_mode', "tab")
        if "window" == mode:
            webbrowser.open_new(url)
        else:
            webbrowser.open_new_tab(url)

    def on_engine_done(self, index):
        if index != -1:
            self.set_engine_setting(self.items[index])
        if self.get_setting('engine_change', False) and self.args['input_panel']:
            sublime.set_timeout(self.show_search_panel, 10)

    def show_engine_panel(self):
        self.items = [k for k in self.get_engines()]
        self.window.show_quick_panel(self.items, self.on_engine_done)


class WebSearchCommand(sublime_plugin.TextCommand,WebSearchCommon):

    def run(self, edit, **args):
        self.args = args
        if self.get_setting('engine_change', False) and args['input_panel']:
            self.window = self.view.window()
            self.args['input_panel'] = False
            sublime.set_timeout(self.show_engine_panel, 10)
        self.search(self.get_text(self.view))

    def is_visible(self):
        return True if len(self.get_text(self.view)) else False

    def description(self, **args):
        type_caption = int(self.get_setting('context_menu_description', 1))
        text_caption = "Web Search"
        engine = get_current_engine()
        if self.get_setting('context_menu_with_children', False):
            engine = args['engine']
            if type_caption == 1:
                type_caption = 2
        if type_caption == 3:
            text = self.get_text(self.view)
            length = int(self.get_setting('context_menu_description_length', 10)) + 3
            text = text if not len(text) > length else text[0:length] + '...'
            text_caption = "Search in %s for '%s'" % (engine, text)
            length_caption = len(engine) + 20
            if len(text_caption) > length_caption:
                text_caption = text_caption[0:length_caption] + '...'
        elif type_caption == 2:
            text_caption = "Search in %s" % (engine)
        return text_caption


class WebSearchEnterCommand(sublime_plugin.WindowCommand,WebSearchCommon):

    def run(self, **args):
        if self.get_setting('engine_change', False) and args['input_panel']:
            sublime.set_timeout(self.show_engine_panel, 10)
        else:
            sublime.set_timeout(self.show_search_panel, 10)

    def show_search_panel(self):
        self.window.show_input_panel(
            'Enter a search text', '', self.on_search_done, None, None)

    def on_search_done(self, text):
        text = text.strip()
        if len(text):
            self.search(text)


class WebSearchEngineCommand(sublime_plugin.WindowCommand,WebSearchCommon):

    def run(self, **args):
        sublime.set_timeout(self.show_engine_panel, 10)


class WebSearchEventListener(sublime_plugin.EventListener):

    def on_new(self, view):
        if is_ST2:
            update_status_bar(view)

    def on_new_async(self, view):
        update_status_bar(view)

    def on_load(self, view):
        if is_ST2:
            update_status_bar(view)

    def on_load_async(self, view):
        update_status_bar()

    def on_clone(self, view):
        if is_ST2:
            update_status_bar(view)

    def on_clone_async(self, view):
        update_status_bar(view)