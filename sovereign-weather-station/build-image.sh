#!/bin/bash
# Turns the official PocketBeagle 2 Debian image into the Sovereign Weather
# Station image without a board in the loop. Same setup.sh, run inside the
# image through an arm64 chroot, so what comes out is what setup.sh produces.
#
#   sudo ./build-image.sh [output-name]
#
# Needs: xz, losetup, sfdisk, blkid, qemu-user-static + binfmt, sha256sum,
#        curl, python3. Linux only.
# Reads:  BASE_URL (official image .img.xz), BASE_SHA256_URL (its checksum)
#         SWS_USER / SWS_PASSWORD (login written to sysconf.txt for first boot)
#         SWS_GIT_REV (recorded in /opt/sws/BUILD.txt)
# Writes: <output-name>.img.xz and <output-name>.img.xz.sha256sum next to it.
set -euo pipefail
[ "$EUID" -eq 0 ] || { echo "run with sudo"; exit 1; }
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${1:-sovereign-weather-station-pocketbeagle2}"
WORK="${WORK:-$(pwd)/work}"

: "${BASE_URL:=https://files.beagle.cc/file/beagleboard-public-2021/images/pocketbeagle2-debian-13.7-iot-v6.18-k3-arm64-2026-09-20-10gb.img.xz}"
: "${BASE_SHA256_URL:=${BASE_URL}.sha256sum}"
: "${SWS_USER:=student}"
: "${SWS_PASSWORD:=buildit}"

mkdir -p "$WORK"; cd "$WORK"
BASE_XZ="$(basename "$BASE_URL")"
BASE_IMG="${BASE_XZ%.xz}"

echo "==> base image"
[ -s "$BASE_XZ" ] || curl -fsSL -o "$BASE_XZ" "$BASE_URL"
curl -fsSL -o base.sha256sum "$BASE_SHA256_URL"
# the published file is "<hash>  <name>"; check the hash against what we have
awk '{print $1"  '"$BASE_XZ"'"}' base.sha256sum | sha256sum -c -
[ -s "$BASE_IMG" ] || xz -dk -T0 "$BASE_XZ"
cp --sparse=always "$BASE_IMG" "$OUT.img"

echo "==> mount"
# One loop device per partition, by offset. Works on hosts where --partscan
# does not create /dev/loopNpM (no udev, containers, CI runners).
PARTS=()
while read -r start size; do
  PARTS+=("$(losetup --find --show --offset $((start * 512)) --sizelimit $((size * 512)) "$OUT.img")")
done < <(sfdisk -J "$OUT.img" | python3 -c '
import json, sys
for p in json.load(sys.stdin)["partitiontable"]["partitions"]:
    print(p["start"], p["size"])')
cleanup() {
  set +e
  umount -R mnt 2>/dev/null
  for l in "${PARTS[@]}"; do losetup -d "$l" 2>/dev/null; done
}
trap cleanup EXIT
# rootfs: the largest ext4. boot firmware: the FAT partition, if there is one
ROOT_PART=""; BOOT_PART=""; ROOT_SIZE=0
for p in "${PARTS[@]}"; do
  case "$(blkid -o value -s TYPE "$p" || true)" in
    ext4) sz=$(blockdev --getsize64 "$p"); [ "$sz" -gt "$ROOT_SIZE" ] && ROOT_PART="$p" && ROOT_SIZE=$sz ;;
    vfat) BOOT_PART="$p" ;;
  esac
done
[ -n "$ROOT_PART" ] || { echo "no ext4 partition in $BASE_IMG"; exit 1; }
mkdir -p mnt
mount "$ROOT_PART" mnt
if [ -n "$BOOT_PART" ]; then
  mkdir -p mnt/boot/firmware; mount "$BOOT_PART" mnt/boot/firmware
fi
echo "    root: $ROOT_PART   boot: ${BOOT_PART:-in rootfs}"
echo "    base: $(cat mnt/etc/dogtag 2>/dev/null || echo '?')"

echo "==> chroot"
QEMU="$(command -v qemu-aarch64-static)"
cp "$QEMU" mnt/usr/bin/
for d in proc sys dev dev/pts; do mount --bind "/$d" "mnt/$d"; done
cp -L /etc/resolv.conf mnt/etc/resolv.conf.build
mv mnt/etc/resolv.conf mnt/etc/resolv.conf.orig 2>/dev/null || true
cp mnt/etc/resolv.conf.build mnt/etc/resolv.conf
# do not let apt start services inside the chroot
printf '#!/bin/sh\nexit 101\n' > mnt/usr/sbin/policy-rc.d; chmod +x mnt/usr/sbin/policy-rc.d

rm -rf mnt/tmp/sws; mkdir -p mnt/tmp/sws
cp -a "$HERE"/setup.sh "$HERE"/station "$HERE"/bin "$HERE"/systemd "$HERE"/test mnt/tmp/sws/
chmod +x mnt/tmp/sws/setup.sh mnt/tmp/sws/bin/*
chroot mnt /usr/bin/env SWS_GIT_REV="${SWS_GIT_REV:-}" DEBIAN_FRONTEND=noninteractive \
  /bin/bash -c 'cd /tmp/sws && ./setup.sh && apt-get clean && rm -rf /var/lib/apt/lists/*'

echo "==> smoke test inside the image (arm64 python under qemu)"
chroot mnt /usr/bin/python3 -c 'import smbus2, sys; sys.path.insert(0,"/opt/sws/station"); import station, bme280, ssd1306; print("    imports ok", sys.version.split()[0])'
chroot mnt /usr/bin/python3 /opt/sws/bin/sws-check >/dev/null 2>&1 || true   # runs, finds no buses here: fine
chroot mnt /bin/bash -c 'systemctl is-enabled station.service sws-firstboot.service fake-hwclock.service' | sed 's/^/    /'
test -x mnt/opt/sws/bin/sws-check && test -x mnt/opt/sws/bin/sws-live && test -x mnt/opt/sws/bin/sws-firstboot
test -L mnt/usr/local/bin/sws-check && test -L mnt/usr/local/bin/sws-live
test -d mnt/data
cat mnt/opt/sws/BUILD.txt | sed 's/^/    /'

echo "==> first-boot login"
SYSCONF=""
for c in mnt/boot/firmware/sysconf.txt mnt/boot/sysconf.txt; do [ -f "$c" ] && SYSCONF="$c" && break; done
if [ -n "$SYSCONF" ]; then
  sed -i -e "s|^#\?user_name=.*|user_name=$SWS_USER|" -e "s|^#\?user_password=.*|user_password=$SWS_PASSWORD|" "$SYSCONF"
  grep -q "^user_name=" "$SYSCONF" || printf 'user_name=%s\nuser_password=%s\n' "$SWS_USER" "$SWS_PASSWORD" >> "$SYSCONF"
  echo "    $SYSCONF: user_name=$SWS_USER"
else
  echo "    no sysconf.txt found; the image keeps the base login"
fi

echo "==> clean up the chroot"
rm -f mnt/usr/sbin/policy-rc.d mnt/usr/bin/qemu-aarch64-static mnt/etc/resolv.conf.build
rm -rf mnt/tmp/sws
mv mnt/etc/resolv.conf.orig mnt/etc/resolv.conf 2>/dev/null || rm -f mnt/etc/resolv.conf
# host keys and machine-id are made unique per board by sws-firstboot on
# first boot. leave the base image's in place so ssh still starts if that
# service is ever disabled.
rm -f mnt/data/.firstboot-done
sync
umount -R mnt; for l in "${PARTS[@]}"; do losetup -d "$l"; done; trap - EXIT

echo "==> compress"
xz -T0 -6 -f "$OUT.img"
sha256sum "$OUT.img.xz" > "$OUT.img.xz.sha256sum"
cat "$OUT.img.xz.sha256sum"
echo "==> done: $WORK/$OUT.img.xz"
