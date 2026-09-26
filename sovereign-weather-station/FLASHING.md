# Flashing twenty cards

Do the [bench test](BENCH-TEST.md) first. Then this is mechanical.

## Get the image once

From https://github.com/OurWorldsXR/build-break-own/releases take the newest
`station-v*` release: `sovereign-weather-station-pocketbeagle2.img.xz` and
the `.sha256sum` beside it. Check it:

```
shasum -a 256 -c sovereign-weather-station-pocketbeagle2.img.xz.sha256sum
```

Keep the `.xz`. Do not decompress it by hand; the tools below read it directly.

## Write cards

**BeagleBoard Imaging Utility** (easiest, any OS). Choose the file, choose
the card, write, wait for verify. About four minutes per card on a USB 3 reader.

**Command line, Mac.** Find the card with `diskutil list` (it is the one that
matches the card's size; get this wrong and you erase the wrong disk).

```
diskutil unmountDisk /dev/diskN
xzcat sovereign-weather-station-pocketbeagle2.img.xz | sudo dd of=/dev/rdiskN bs=4m status=progress
sudo diskutil eject /dev/diskN
```

**Command line, Linux.** Find the card with `lsblk`.

```
xzcat sovereign-weather-station-pocketbeagle2.img.xz | sudo dd of=/dev/sdX bs=4M status=progress conv=fsync
```

Two USB card readers and two terminals halves the time. Twenty cards is
roughly 45 minutes with two readers.

## Label as you go

Number the cards 1 to 20 with a paint marker. Number the boards 1 to 15 to
match. A card that has been booted once carries that board's name, host keys
and data, so keep card and board together from the first boot onwards.

## First boot, per board

Each card is identical until it boots. On its first boot the board:

1. creates the `student` login from `sysconf.txt` on the card, then blanks that file
2. generates its own ssh host keys and machine id
3. names itself `sws-` plus six random characters, and writes that to `/data/station-id`
4. starts the logger

Boot every board once before the workshop, on a bench, with the sensor and
screen attached. Confirm the screen comes up. That is the whole per-board
test. It takes about a minute each and finds dead cards and dead boards before
students do.

## The login

`student` / `buildit`. It is printed in this repo, so it is not a secret. If a
board is going somewhere the login matters, `passwd` on that board. If you
want a different default baked into the image, set the `SWS_PASSWORD` secret
in the GitHub repository and push a new `station-v*` tag.

## Spares

Five cards more than boards. Flash all twenty. A card that fails at the
workshop gets swapped, not debugged.
