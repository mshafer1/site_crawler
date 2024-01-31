import logging
import string
import urllib.parse

import selenium.webdriver.chrome.options as chrome_options
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from seleniumrequests import Chrome


class Session:
    def __init__(self, driver_path="chromedriver", use_headless=False):
        self._opts = chrome_options.Options()
        if use_headless:
            self._opts.add_argument("--headless")
            self._opts.add_argument("--disable-gpu")
        self._browser_logger = logging.getLogger("chrome")
        self._browser = Chrome(options=self._opts)
        self._browser.set_page_load_timeout(30)

    def close(self):
        self._browser.close()

    def get(self, url):
        self._browser.get(url)

    @property
    def browser(self):
        return self._browser

    @staticmethod
    def authenticate(sign_in_url):
        session = Session()
        session.get(sign_in_url)
        input("Press enter once page is ready...")

        return session


def on_same_domain(other: str, current: str):
    """Return if other and current are on the same domain.

    >>> on_same_domain("/foo", "example.com")
    True

    >>> on_same_domain("/foo", "https://example.com/bar/baz")
    True

    >>> on_same_domain("//example.com/foo", "example.com")
    True

    >>> on_same_domain("//www.example.com/foo", "example.com")
    False

    >>> on_same_domain("https://www.example.com/foo", "example.com")
    False

    >>> on_same_domain("https://example.com/foo", "example.com")
    True
    """
    if other is None:
        return False

    if other.startswith("/") and not other.startswith("//"):
        return True

    if "/" not in current:
        current_domain = current
    else:
        current_domain = urllib.parse.urlparse(current).netloc

    other_domain = urllib.parse.urlparse(other).netloc

    return current_domain == other_domain


class Spider:
    def __init__(self, starting_page):
        self._seen = set()
        self._to_visit = set()

        self._session = Session.authenticate(starting_page)

        self._starting_domain = urllib.parse.urlparse(
            self._session.browser.current_url
        ).netloc

    @property
    def seen(self):
        return self._seen

    @property
    def to_visit(self):
        return self._to_visit

    @property
    def starting_domain(self):
        return self._starting_domain

    def _visit(self, action: callable):
        action(
            url=self._session.browser.current_url,
            log=tuple(self._session.browser.get_log("browser")),
            page=BeautifulSoup(self._session.browser.page_source, "html.parser"),
        )

    def crawl(self, action: callable):
        current_links = self._session.browser.find_elements(by=By.XPATH, value="//a")

        self.to_visit.update(
            [
                link.get_attribute("href")
                for link in current_links
                if on_same_domain(link.get_attribute("href"), self.starting_domain)
            ]
        )

        def _get_link():
            try:
                return self.to_visit.pop()
            except KeyError:
                return None

        while link := _get_link():
            href = link
            if href.startswith("/"):
                href = self.starting_domain + href

            self._session.get(href)
            self._visit(action=action)

            self.seen.update([link, href, self._session.browser.current_url])

            current_links = self._session.browser.find_elements(
                by=By.XPATH, value="//a"
            )

            links = set(
                filter(None, [link.get_attribute("href") for link in current_links])
            )
            links = links - self.seen
            # links = {l for l in links if ("." not in l.rsplit("/", maxsplit=1)[-1] or l.endswith("/") or l.endswith(".html"))}
            links = {l for l in links if on_same_domain(l, self.starting_domain)}
            self.to_visit.update(links)

        print("Finished. Visited", len(self._seen), "pages.")
