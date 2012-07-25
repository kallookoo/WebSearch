# WebSearch

A [Sublime Text 2](http://www.sublimetext.com/2) plugin that performs a 
web search of current selected text.

By default `Google` is used for web searches but the search provider is
configurable in the plugin settings.

# Installation

Just clone WebSearch repository under your ST2 Packages folder.

# Configuration

To change search the provider just change the value of `search_url` 
configuration key.

For example to use `DuckDuckGo` instead of `Google` change `search_url` to:

    {
        "search_url": "http://duckduckgo.com/?q="
    }
