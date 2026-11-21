"""Share row on chosen pages: open on your phone (QR), email me this link, share (19 Nov 2026).

Nothing is sent to arcroad: the QR code is a picture made at build time, the email link opens the
visitor's own mail app, and Share uses the device's own share sheet (or copies the link). No form,
no phone number, no storage. Idempotent: rerunning replaces the block between its markers.
Run from the repo root: python3 tools/share_block.py
"""
import html
import os
import re
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web")
PAGES = {
    "field/index.html": "field",
    "moves/index.html": "moves",
    "cost/index.html": "cost",
}
BLOCK = re.compile(r"<!-- share:start -->.*?<!-- share:end -->\n?", re.S)
NOTE = ("Nothing you do here is sent to us or stored. "
        "The link opens in your own phone, email or share app.")


def block(slug: str, title: str) -> str:
    url = f"https://arcroad.org/{slug}/"
    mail = f"mailto:?subject={quote('arcroad: ' + title)}&body={quote(url)}"
    t = html.escape(title, quote=True)
    return (
        '<!-- share:start --><section class="ar-share" aria-label="Keep this page">'
        f'<details class="ar-share-qr"><summary>Open on your phone</summary>'
        f'<img src="/share/{slug}.svg" width="168" height="168" alt="QR code that opens {url}">'
        '<span>Point your phone camera at the code.</span></details>'
        f'<a class="ar-share-btn" href="{html.escape(mail, quote=True)}">Email me this link</a>'
        f'<button class="ar-share-btn" type="button" data-ar-share data-url="{url}" data-title="{t}">Share</button>'
        f'<p class="ar-share-note">{NOTE}</p>'
        '<script src="/share.js" defer></script></section><!-- share:end -->\n'
    )


def apply(page: str, slug: str) -> str:
    m = re.search(r"<title>(.*?)</title>", page, re.S)
    title = html.unescape(m.group(1)).replace("arcroad · ", "").strip() if m else "arcroad"
    page = BLOCK.sub("", page)
    i = page.rfind("<footer")
    if i < 0:
        raise SystemExit("no footer found")
    j = page.rfind("\n", 0, i) + 1
    return page[:j] + block(slug, title) + page[j:]


def main() -> None:
    for rel, slug in PAGES.items():
        path = os.path.join(WEB, rel)
        with open(path, encoding="utf-8") as fh:
            old = fh.read()
        new = apply(old, slug)
        if new != old:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(new)
            print("share:", rel)


if __name__ == "__main__":
    main()
