import functools
import logging
import pathlib
import textwrap
import typing

import black
import click
from bs4 import BeautifulSoup
from decouple import config

import site_crawler

SITE_TO_CRAWL = config("SITE_TO_CRAWL")

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


def _visit(
    url,
    page: BeautifulSoup,
    *_,
    log=tuple(),
    print_images=False,
    print_links=False,
    print_scripts=False,
    print_log_messages=False,
    **__,
):
    images = []
    links = []
    scripts = []
    console_messages = []

    if print_log_messages:
        console_messages = log

    if print_images:
        dom_images = page.find_all("img")
        images = list(filter(None, [img.attrs.get("src") for img in dom_images]))

    if print_links:
        dom_links = page.find_all("a")
        links = list(filter(None, [link.attrs.get("href") for link in dom_links]))

    if print_scripts:
        dom_scripts = page.find_all("script")
        scripts = list(filter(None, [str(script) for script in dom_scripts]))

    content_lines = []
    _formatting_config = black.Mode()
    for name, thing in [
        ("Images", images),
        ("Links", links),
        ("Scripts", scripts),
        ("Log messages", console_messages),
    ]:
        if thing:
            content_lines.append(f"{name}: ")
            content_lines.extend(
                black.format_str(str(thing), mode=_formatting_config).splitlines()
            )
            content_lines.append("\n")
            content_lines.append("\n")

    _logger.info(
        "Page -> %s\n%s", url, textwrap.indent("\n".join(content_lines), " " * 4)
    )


@click.command("site-crawler")
@click.option(
    "--print-images",
    is_flag=True,
    help="Print the sources for images found on each page",
)
@click.option("--print-links", is_flag=True, help="Print the links found on each page")
@click.option(
    "--print-scripts", is_flag=True, help="Print the scripts found on each page"
)
@click.option(
    "--print-log-messages",
    is_flag=True,
    help="Print the log messages from the browser for each page",
)
@click.option("--print-everything", is_flag=True, help="Shortcut to turn everything on")
@click.option(
    "--log-file", type=click.Path(dir_okay=False, writable=True, path_type=pathlib.Path)
)
def _main(
    print_images: bool,
    print_links: bool,
    print_log_messages: bool,
    print_scripts: bool,
    print_everything: bool,
    log_file: typing.Optional[pathlib.Path],
):
    log_format = "%(asctime)s::%(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)
    if log_file:
        file_logger = logging.FileHandler(log_file, mode="w", encoding="utf-8")
        file_logger.setFormatter(logging.Formatter(log_format))
        _logger.addHandler(file_logger)

    _logger.info("Opening Chrome...")
    spider = site_crawler.Spider(SITE_TO_CRAWL)

    _logger.info("Starting to crawl...")
    spider.crawl(
        action=functools.partial(
            _visit,
            print_images=print_images or print_everything,
            print_links=print_links or print_everything,
            print_log_messages=print_log_messages or print_everything,
            print_scripts=print_scripts or print_everything,
        )
    )


if __name__ == "__main__":
    _main()
