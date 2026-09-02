# Getting this onto GitHub

## Make the repo

github.com/OurWorldsXR, new repository.

**Name:** `build-break-own`

**Description:** A weather station that answers to nobody. Digital sovereignty,
built by hand, for high school. OurWorlds and BeagleBoard, AISES 2026.

Public. Do not let GitHub add a README, a .gitignore or a licence. They are
already here and they are not the defaults.

## Push it

The repo already exists. Clone it, unzip the files into it, push.

### Windows, PowerShell

```powershell
git clone https://github.com/OurWorldsXR/build-break-own.git
Expand-Archive -Path "$HOME\Downloads\build-break-own.zip" -DestinationPath .\build-break-own -Force
cd build-break-own
git add -A
git commit -m "Build It, Break It, Own It: curriculum, worksheet, station image"
git push origin main
```

`Expand-Archive` keeps the dot files. `git add -A` picks them up. Check for
them before you commit:

```powershell
git status --short
```

You should see `.nojekyll` and `.github/ISSUE_TEMPLATE/review.md` in that list.
Without `.nojekyll`, GitHub runs Jekyll over the HTML and things break quietly.

### macOS or Linux

```bash
git clone https://github.com/OurWorldsXR/build-break-own.git
unzip -o ~/Downloads/build-break-own.zip -d build-break-own
cd build-break-own
git add -A
git commit -m "Build It, Break It, Own It: curriculum, worksheet, station image"
git push origin main
```

If the default branch is `master` rather than `main`, push to that or rename it
with `git branch -M main` first.

## Turn on Pages

This is the step that matters. Without it, everything in the repo is source
code. With it, `index.html` is a webpage.

Settings, then Pages, then Deploy from a branch, `main`, `/ (root)`.

Live at `https://ourworldsxr.github.io/build-break-own/` in a minute or two.

Put that URL in the About box on the repo, top right. It shows next to the
description, and it is the first thing a reviewer will click.

**Send people the Pages link, not the repo link.** Clicking `index.html` inside
GitHub shows the source, not the page. Same for `worksheet.html` and
`teacher-guide.html`. The markdown files render fine either way.

If you cannot turn Pages on for some reason, send a zip of the folder instead.
Everything works from the filesystem, so a zip is a fine review copy and it
forces the offline test at the same time.

## Then

**Topics:** `indigenous-data-sovereignty` `stem-education` `beagleboard`
`curriculum` `open-hardware` `aises`

**About, Website:** the Pages URL.

**Issues on.** There is a review template so people get a form instead of a
blank box. Wiki, Projects and Discussions off.

## Asking for the review

Add the AUNTIE reviewers as collaborators. Point them at the repo root. The
README opens with what needs checking, so they do not have to hunt for it.

Then file the checklist as issues yourself, one per line, before you send the
link. An open issue is something a person can pick up in ten minutes. A bullet
in a README is something everybody assumes somebody else is doing.

Ask for issues rather than notes. Nothing gets lost between now and 14 October
that way.

## When the corrections land

Drop the draft line at the top of the README. Then tag it:

```bash
git tag -a v1.0-aises2026 -m "as taught, Portland, 14 October 2026"
git push --tags
```

Then take it to BeagleBoard, per beagleboard.org/project-guidelines.
