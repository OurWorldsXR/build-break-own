#!/usr/bin/env python3
"""Put a real photograph inside the scroller without breaking offline use.

    python3 embed-image.py typewriter.jpg buildit-scroller.html typewriter

Reads the image, base64s it, and writes it into the IMG registry. The file
stays a single self-contained document that works from a USB stick.

Keep the source image under about 400 KB or the HTML gets unwieldy. A
1600px-wide JPEG at quality 70 is usually plenty, since it sits behind text
at low opacity.
"""
import base64, mimetypes, sys, pathlib

if len(sys.argv) != 4:
    sys.exit(__doc__)

img_path, html_path, key = sys.argv[1], sys.argv[2], sys.argv[3]
data = pathlib.Path(img_path).read_bytes()
mime = mimetypes.guess_type(img_path)[0] or "image/jpeg"
uri = "data:%s;base64,%s" % (mime, base64.b64encode(data).decode())

html = pathlib.Path(html_path).read_text()
needle = "  %s:''" % key
if needle not in html:
    # already populated: replace whatever is there
    import re
    pat = re.compile(r"(\n  %s:')[^']*(')" % re.escape(key))
    if not pat.search(html):
        sys.exit("could not find '%s' in the IMG registry of %s" % (key, html_path))
    html = pat.sub(lambda m: m.group(1) + uri + m.group(2), html)
else:
    html = html.replace(needle, "  %s:'%s'" % (key, uri), 1)

pathlib.Path(html_path).write_text(html)
kb = len(uri) / 1024
print("embedded %s as '%s'  (%.0f KB of base64)" % (img_path, key, kb))
if kb > 600:
    print("that is large. consider re-exporting the JPEG smaller.")
