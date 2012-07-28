import sublime
import sublime_plugin
import webbrowser

settings = sublime.load_settings('WebSearch.sublime-settings')


class WebSearchCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        webbrowser.open_new_tab(settings.get('search_url') +
            self.selected_text())

    def is_enabled(self):
        return bool(self.selected_text())

    def selected_text(self):
        l = []
        for sel in self.view.sel():
            l.append(self.view.substr(sel))
        return ' '.join(l)
