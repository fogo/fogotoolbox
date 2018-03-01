"""
So I was writing this huge guide in markdown and felt it'd nice to have
a table of contents w/ internal links to headers in markdown file.

It is pretty raw and simple script, maybe I'll improve it over time.

Currently, everything is based on
[gitlab markdown style](https://docs.gitlab.com/ee/user/markdown.html),
as it was the platform I was using at the time.
"""

import re

from typing import Union, Iterator

# Based on https://docs.gitlab.com/ee/user/markdown.html#header-ids-and-links
forbidden_chars = r"[\(\):\",\?\-\.]+"


def md_table_contents(md: str) -> str:
    """
    Generates a table of contents for every header found in Markdown text.

    Searches for lines starting with "#" and replaces forbidden chars in
    internal references.
    """
    return "\n".join(_header_to_item(header) for header in _iter_headers(md))


def _header_line(line: str) -> Union[None, tuple]:
    """
    If it is detected as header line, returns its header level and caption.
    Otherwise returns `None`.
    """
    m = re.match(r"^(#+)(.+)", line)
    if m:
        level = len(m.group(1))
        caption = m.group(2)
        return level, caption

    return None


def _caption_to_link(caption: str) -> str:
    """
    Performs necessary replacements so caption can be converted to a proper
    internal link.
    """
    link = caption
    link = link.lower()
    link = link.strip()
    link = re.sub(forbidden_chars, "", link)
    link = re.sub(r"\s+", "-", link)
    link = link.lstrip("-")
    return "#" + link


def _header_to_item(header: str) -> str:
    """
    Converts a header line to an item in table of contents.
    """
    level, caption = header
    link = _caption_to_link(caption)

    full_link = "{bullet} [{caption}]({link})".format(
        caption=caption.strip(),
        link=link,
        bullet="{}*".format("  " * (level - 1))
    )

    return full_link


def _iter_headers(md_contents: str) -> Iterator[str]:
    """
    Iterates only lines that contain a header.
    """
    for line in md_contents.splitlines():
        header = _header_line(line)
        if header is None:
            continue

        yield header
