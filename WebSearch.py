import sublime
import sublime_plugin
import webbrowser
import re

try:
    # Python 3
    from urllib import quote as url_text_encode
except ImportError:
    # Python 2
    from urllib.parse import quote_plus as url_text_encode

class WebSearchCommon(object):

    engine_url = ''

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
        settings.set('active', engine)

    def get_engines(self):
        engines = {
            "Ask": "https://www.ask.com/web?q=",
            "Bing": "https://www.bing.com/search?q=",
            "DuckDuckGo": "https://duckduckgo.com/?q=",
            "Google": "https://google.com/search?q=",
            "Wikipedia": "https://wikipedia.org/w/index.php?search=",
            "Yahoo": "https://search.yahoo.com/search?p="
        }
        if self.get_setting('engines_for_sources', False):
            dev_engines = {
                "MDN": "https://developer.mozilla.org/search?q=",
                "PHP": "https://php.net/search.php?show=quickref&pattern=",
                "Python": "https://docs.python.org/3/search.html?q=",
                "Python2": "https://docs.python.org/2/search.html?q=",
                "WordPress": "https://developer.wordpress.org/?s="
            }
            engines.update(dev_engines)
        user_engines = self.get_setting('engines', {})
        if len(user_engines):
            engines.update(user_engines)
        return engines

    def get_engine(self, name):
        engines = self.get_engines()
        return '' if not name in engines else engines[name]

    def search(self, text, url):
        if url.startswith('http') and len(text):
            self.webbrowser(url + url_text_encode(text))

    def webbrowser(self, url):
        mode = self.get_setting('browser_mode', "tab")
        if "window" == mode:
            webbrowser.open_new(url)
        else:
            webbrowser.open_new_tab(url)

    def on_engine_done(self, index):
        self.engine_url = ''
        if index != -1:
            self.set_engine_setting(self.items[index])
            # self.engine_url = self.get_engine(self.items[index])
        if self.get_setting('engine_change', False) and self.args['input_panel']:
            sublime.set_timeout(self.show_search_panel, 10)

    def show_engine_panel(self):
        self.items = list()
        for k in self.get_engines():
            self.items.append(k)
        self.items.sort()
        self.window.show_quick_panel(self.items, self.on_engine_done)


class WebSearchCommand(sublime_plugin.TextCommand,WebSearchCommon):

    def run(self, edit, **args):
        self.args = args
        if self.get_setting('engine_change', False) and args['input_panel']:
            self.window = self.view.window()
            self.args['input_panel'] = False
            sublime.set_timeout(self.show_engine_panel, 10)
        self.engine_url = self.get_engine(self.get_setting('active', 'Google'))
        self.search(self.get_text(self.view), self.engine_url)

    def is_visible(self):
        return True if len(self.get_text(self.view)) else False

    def description(self, **args):
        type_caption = int(self.get_setting('context_menu_description', 1))
        text_caption = "Web Search"
        if type_caption == 3:
            text = self.get_text(self.view)
            engine = self.get_setting('active', 'Google')
            length = int(self.get_setting('context_menu_description_length', 10)) + 3
            text = text if not len(text) > length else text[0:length] + '...'
            text_caption = "Search in %s for '%s'" % (engine, text)
            length_caption = len(engine) + 20
            if len(text_caption) > length_caption:
                text_caption = text_caption[0:length_caption] + '...'
        elif type_caption == 2:
            text_caption = "Search in %s" % (self.get_setting('active', 'Google'))
        return text_caption


class WebSearchEnterCommand(sublime_plugin.WindowCommand,WebSearchCommon):

    def run(self, **args):
        self.args = args
        if self.get_setting('engine_change', False) and self.args['input_panel']:
            sublime.set_timeout(self.show_engine_panel, 10)
        else:
            sublime.set_timeout(self.show_search_panel, 10)

    def show_search_panel(self):
        self.window.show_input_panel(
            'Enter a search text', '', self.on_search_done, None, None)

    def on_search_done(self, text):
        text = text.strip()
        if len(text):
            if self.get_setting('engine_change', False) and self.args['input_panel']:
                self.search(text, self.engine_url)
            else:
                self.search(text, self.get_engine(self.get_setting('active', 'Google')))


class WebSearchEngineCommand(sublime_plugin.WindowCommand,WebSearchCommon):

    def run(self, **args):
        self.args = args
        sublime.set_timeout(self.show_engine_panel, 10)