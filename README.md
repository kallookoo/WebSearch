# WebSearch

[Sublime Text](https://www.sublimetext.com) plugin to web search selected text.

By default Google is used for web searches, but the search engine is configurable.

# Installation (Do not install, it is in development)

Using [Package Control](http://wbond.net/sublime_packages/package_control)
    - From command palette `Package Control: Install Package`
    - Look for "WebSearch"
    - Restart Sublime Text

# Usage

- Select a block of text
- Using keyboard: `ctrl+shif+g`
- Using mouse: `Right click > Search <SelectedSearchEngine> for '<Text>'`

# Settings

### Change default search engine

- Open `Preferences > Package Settings > Web Search > Settings - User`
- Change `active` configuration key to one supported search engines
    - Google
    - DuckDuckGo
    - Yahoo
    - Bing
    - Ask
    - Wikipedia

Code:

    {
        // use DuckDuckGo for web searches
        "active": "DuckDuckGo"
    }

### Add a new search engine

- Open `Preferences > Package Settings > Web Search > Settings - Default`
- Add a new entry under `engines`

Code:

    {
        "engines": 
        {
            "Google": "http://google.com/search?q=",
            "DuckDuckGo": "http://duckduckgo.com/?q=",
            "Yahoo": "http://search.yahoo.com/search?p=",
            "Bing": "http://www.bing.com/search?q=",
            "Ask": "http://www.ask.com/web?q=",
            "Wikipedia": "http://wikipedia.org/w/index.php?search=",
            "<SearchEngineName>": "<SearchUrl>" // new
        },
        "active": "Google"
    }

### Change default keyboard shortcut

- Open `Preferences > Package Settings > Web Search > Key Bindings - User` 
- Change default key binding for `web_search` command

Code:

    [
        { "keys": ["ctrl+shift+w"], "command": "web_search" }
    ]
