"""Check rendered navigation and assets, including staging path isolation."""

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls: list[str] = []

    def handle_starttag(self, tag, attrs):
        self.urls.extend(value for key, value in attrs if key in ("href", "src") and value)


def check(root: Path, base: str) -> None:
    base_parts = urlsplit(base)
    prefix = base_parts.path.rstrip("/") + "/"
    staging = prefix.endswith("/staging/")
    for relative in ("index.html", "about/index.html", "contact/index.html", "login/index.html", "404.html"):
        if not (root / relative).is_file():
            raise ValueError(f"Missing page: {relative}")
    for document in root.rglob("*.html"):
        html = document.read_text()
        if staging and 'content="noindex, nofollow"' not in html:
            raise ValueError(f"Staging page is indexable: {document}")
        parser = Links()
        parser.feed(html)
        for link in parser.urls:
            target = urlsplit(urljoin(base + "/" + str(document.relative_to(root)), link))
            if target.netloc != base_parts.netloc or target.scheme not in ("http", "https"):
                continue
            # The staging notice intentionally links to the production homepage.
            if staging and link == "https://building20.vc/":
                continue
            target_path = target.path or "/"
            if target_path == prefix.rstrip("/"):
                target_path += "/"
            if not target_path.startswith(prefix):
                raise ValueError(f"Link escapes {prefix}: {document}: {link}")
            local = root / unquote(target_path.removeprefix(prefix))
            if local.is_dir():
                local /= "index.html"
            if not local.is_file():
                raise ValueError(f"Broken link: {document}: {link}")
    for css in root.glob("*.css"):
        for raw in re.findall(r"url\(([^)]+)\)", css.read_text()):
            link = raw.strip("\"' ")
            if link.startswith(("data:", "https:", "http:")):
                continue
            if link.startswith("/") or not (css.parent / link).is_file():
                raise ValueError(f"Missing or root-relative CSS asset: {css}: {link}")
    print(f"Verified pages, links, assets and indexing policy: {base}")


if __name__ == "__main__":
    check(Path(sys.argv[1]), sys.argv[2])
