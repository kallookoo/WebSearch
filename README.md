# WebSearch

A simple [Sublime Text 2](http://www.sublimetext.com/2) plugin used to do a 
web search of current selected text. By default Google is used for web searches
but the search provider is configurable.

# Installation

1. Manually
    - Download an [archive](https://github.com/catalinc/WebSearch/zipball/master) of Web Search
    - Extract archive contents under `ST2/Packages/WebSearch` directory 
      (use `Preferences > Browse Packages...` to locate ST2/Packages directory) 
2. Using git repository on github
    - Open an terminal, cd to ST2/Packages directory
    - `git clone https://github.com/catalinc/WebSearch`
3. Using [Package Control](http://wbond.net/sublime_packages/package_control) (pending)
    - From command palette `Package Control: Install Package`
    - Look for "WebSearch"

# Usage

- Select a block of text
- Using keyboard: `ctrl+shif+g`
- Using mouse: `Right click > Web Search`

# Settings

### Change default search provider

- Open `Preferences > Package Settings > Web Search > Settings - User`
- Change the value of `search_url` configuration key

Code:

    {
        // use DuckDuckGo instead of Google for searches
        "search_url": "http://duckduckgo.com/?q="
    }

### Change default keyboard shortcut

- Open `Preferences > Package Settings > Web Search > Key Bindings - User` 
- Change default key binding for `web_search` command

Code:

    [
        { "keys": ["ctrl+shift+w"], "command": "web_search" }
    ]
