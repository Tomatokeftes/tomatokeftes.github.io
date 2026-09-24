"""Make the picture that link previews of the site show (LinkedIn, Slack, and so on).

    python _tools/social_card.py

Lays out the card in HTML (name, role, and the Summer Mountains ink from
assets/img/mountains-summer.webp on scroll paper) and has a headless Edge or
Chrome take a 1200x630 screenshot of it, written to assets/img/social-card.png.
_config.yml makes it the default preview image of every page.
"""

import base64
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from PIL import Image

SITE = Path(__file__).resolve().parent.parent
OUT = SITE / "assets" / "img" / "social-card.png"
BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "google-chrome", "chromium", "chromium-browser", "microsoft-edge",
]

CARD = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600&family=EB+Garamond:ital,wght@0,500;1,400&display=swap">
<style>
  html, body { margin: 0; width: 1200px; height: 630px; overflow: hidden; background: #f4eee3; }
  .mount { position: absolute; inset: 22px; border: 1px solid #bfb09a; outline: 1px solid #d8cdbb; outline-offset: -9px; }
  .mountains { position: absolute; right: 44px; bottom: 44px; width: 640px; aspect-ratio: 1120 / 517; background: #3a332c;
    -webkit-mask: url(data:image/webp;base64,%(mask)s) center / 100%% 100%% no-repeat; }
  .text { position: absolute; left: 88px; top: 92px; color: #1f1b17; }
  h1 { margin: 0; font: 600 108px/0.94 "Cormorant Garamond", serif; }
  p { margin: 26px 0 0; font: italic 400 32px/1.35 "EB Garamond", serif; color: #5c5247; }
  .site { position: absolute; left: 88px; bottom: 76px; margin: 0; font: 500 27px "EB Garamond", serif;
    font-variant-caps: all-small-caps; letter-spacing: 0.1em; color: #9a4b3d; }
</style></head>
<body>
  <div class="mount"></div>
  <div class="mountains"></div>
  <div class="text">
    <h1>Theodoros<br>Visvikis</h1>
    <p>PhD candidate, M4i, Maastricht University<br>Mass spectrometry imaging and spatial omics</p>
  </div>
  <p class="site">tomatokeftes.github.io</p>
</body></html>
"""


def browser():
    for candidate in BROWSERS:
        found = shutil.which(candidate) or (candidate if Path(candidate).is_file() else None)
        if found:
            return found
    raise SystemExit("Needs Microsoft Edge or Google Chrome to draw the card.")


def main():
    mask = base64.b64encode((SITE / "assets" / "img" / "mountains-summer.webp").read_bytes()).decode()
    # the browser's background process can still hold its profile when we finish, hence ignore_cleanup_errors
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        page = Path(tmp) / "card.html"
        page.write_text(CARD % {"mask": mask}, encoding="utf-8")
        shot = Path(tmp) / "card.png"
        subprocess.run(
            [browser(), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
             "--user-data-dir=" + str(Path(tmp) / "profile"), "--virtual-time-budget=5000",
             "--window-size=1200,630", "--screenshot=" + str(shot), page.as_uri()],
            check=True, capture_output=True, timeout=120,
        )
        # on Windows the browser hands the work to a background process and returns at once
        for _ in range(120):
            if shot.exists() and shot.stat().st_size > 0:
                time.sleep(1)
                break
            time.sleep(0.5)
        else:
            raise SystemExit("The browser did not write the card.")
        Image.open(shot).convert("RGB").save(OUT, optimize=True)
    print("Wrote %s (%d KB)" % (OUT.relative_to(SITE), OUT.stat().st_size // 1024))


if __name__ == "__main__":
    main()
