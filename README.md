# WebSearch

[Sublime Text](https://www.sublimetext.com) plugin to search on World Wide Web.

This package adds:

* A `Web Search` command to the context menu on the view.
* A command palette for the current selection or word
* A command palette that will ask you what to search
* A command palette for change engine during session (Close Sublime Text, return to active engine)

By default Google is used for web searches, but the search engine is configurable.

# Installation

Using git repository on github

- Open an terminal, cd to Sublime Text/Packages directory
- `git clone https://github.com/kallookoo/WebSearch`

Using [Package Control](http://wbond.net/sublime_packages/package_control) "Not available"

- From command palette `Package Control: Install Package`
- Look for "WebSearch"

## Usage

- Using context menu on view, see `context_menu_description` option
- Place the cursor inside a word or select some text and press `Ctrl+Shift+s`.
- Using Command Pallete:
  Find WebSearch... and select available options

# Settings

    {
        // Select current engine
        "active": "Google",
        // Include Sources engines
        // They are the ones that have occurred to me ;)
        // Current available:
        //     "MDN": "https://developer.mozilla.org/search?q=",
        //     "PHP": "https://php.net/search.php?show=quickref&pattern=",
        //     "Python": "https://docs.python.org/3/search.html?q=",
        //     "WordPress": "https://developer.wordpress.org/?s="
        "engines_for_sources": true,
        // Default engines defined inside of plugin
        // is possible overwritte any engine using same name
        // "engines":
        // {
        //     "Ask": "https://www.ask.com/web?q=",
        //     "Bing": "https://www.bing.com/search?q=",
        //     "DuckDuckGo": "https://duckduckgo.com/?q=",
        //     "Google": "https://google.com/search?q=",
        //     "Wikipedia": "https://wikipedia.org/w/index.php?search=",
        //     "Yahoo": "https://search.yahoo.com/search?p="
        // },
        // Show context menu with different caption:
        // 1 - default text caption "Web Search"
        // 2 - Custom text "Search on <engine>"
        // 3 - Custom text with excerpt "Search on <engine> for <excerpt>..."
        "context_menu_description": 3,
        // Length of the selected text for view in context menu
        "context_menu_description_length": 10,
        // Mode to open browser, tab or window
        "browser_mode": "tab",
        // Command Pallete change engine
        // Change engine before search
        "engine_change": false
    }

### Add a new or rewritte exists search engine

- Open `Preferences > Package Settings > Web Search > Settings - User`
- Add a new entry under `engines`

Code:

    {
        "engines": {
            "EngineName": "EngineUrl"
        }
    }

### Available keyboard shortcut

- For launch search `ctrl+shift+s`
- For launch search with custom query `ctrl+alt+s`
- For change active engine only on current session `ctrl+shift+e`

### Change default keyboard shortcut

Open `Preferences > Package Settings > Web Search > Key Bindings - User`