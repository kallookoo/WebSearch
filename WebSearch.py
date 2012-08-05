import sublime
import sublime_plugin
import webbrowser

settings = sublime.load_settings('WebSearch.sublime-settings')


class WebSearchCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        active_engine = settings.get('active')
        search_url = settings.get('engines').get(active_engine, 'Google')
        webbrowser.open_new_tab(search_url + self.selected_text())

    def is_enabled(self):
        return bool(self.selected_text())

    def selected_text(self):
        l = []
        for sel in self.view.sel():
            l.append(self.view.substr(sel))
        return ' '.join(l)

    def description(self):
        text = self.selected_text()
        if len(text) > 31:
            text = text[0:31] + "..."
        return  "Search %s for '%s'" % (settings.get('active'), text)
