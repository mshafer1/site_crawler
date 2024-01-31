# site-crawler
Is a utility for web-crawling a particular site for inspection.

With flags, image sources, or links, or script (or any combination and "everything") can be printed out for each page visited.

`--log-file` is also supported for logging all info to a file for review.

## Installation

Requirements: 
- [Python](https://pthon.org) 
- [poetry](https://python-poetry.org) are already installed and setup
- [Google Chrome](https://www.google.com/chrome/) (the browser that will be used)
- [Chromedrive](https://googlechromelabs.github.io/chrome-for-testing/) (must accessible via the system PATH variable or in the cwd) (NOTE: the version of chromedriver MUST match the currently installed version of Google Chrome)

1. `git clone https://github.com/mshafer1/site_crawler.git`

1. `cd site_crawler`

1. `poetry install --only main`

1. `poetry run site-crawler https://example.com` (substituting the URL for the desired site)