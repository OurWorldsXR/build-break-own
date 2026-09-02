# Photographs

The scroller draws everything on canvas. Photographs are the one exception, and
they get embedded as base64 so the file stays a single offline document.

```
python3 tools/embed-image.py typewriter.jpg buildit-scroller.html typewriter
```

Empty registry entries are fine. Any scene using a photo that is not loaded
falls back to a plain field, so nothing breaks.

---

## What we need first

**`typewriter`**. sits behind all twelve question pages, at 55% opacity under a
blue wash and a heavy vignette. It is atmosphere, not subject. The type has to
stay readable on top of it.

What works:
- Shot from above or at a shallow angle, so the keys read as texture
- A sheet of paper in the platen, ideally blank
- Dark or neutral background, not a bright white studio cut-out
- Wide rather than square, since it is cropped to fill a 16:9 frame
- Under about 400 KB as a JPEG. 1600px wide at quality 70 is plenty

---

## Where to get one, licence-clear

**Smithsonian Open Access**. `si.edu/openaccess`
Millions of items released CC0. The National Museum of American History holds
typewriters. CC0 means no attribution required, though crediting is good manners.

**Library of Congress**. `loc.gov/free-to-use`
Large holdings of early 20th century photographs, many with no known
restrictions. This is also where the Passamaquoddy recordings in this
curriculum come from, so it is a source the piece already leans on.

**Rawpixel public domain collection**. `rawpixel.com/board/537381/public-domain`
Restored public domain photography, well scanned.

**Unsplash**. `unsplash.com`
Free to use commercially without permission. Not public domain, but the licence
is permissive and clear. Largest selection of modern typewriter photography.

**Wikimedia Commons**. check each file individually. Licences vary from CC0 to
share-alike, and share-alike would impose conditions on the whole piece. If you
use Commons, read the specific file page.

---

## What to avoid

Google Images results, Pinterest, stock previews with watermarks, and anything
where the licence is not stated on the page you got it from. In a curriculum
about knowing who controls what you are holding, an unlicensed image would be
the wrong kind of irony.

---

## Other slots worth filling later

These are not wired up yet. Say the word and they can be.

| Key | Scene | Likely source |
|---|---|---|
| `cylinder` | Passamaquoddy 1890 | Library of Congress, American Folklife Center |
| `shiprock` | Fairchild plant | Ask the Computer History Museum. The 1969 brochure is probably still in copyright |
| `mast` | Tribal Digital Village | Ask SCTDV directly. Their photos, their call |

For the last two, the correct move is to write and ask. That is slower, and it
is the curriculum practising what it teaches.
