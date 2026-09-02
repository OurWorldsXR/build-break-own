#!/bin/bash
# Turns an official BeagleBoard.org PocketBeagle 2 Debian image into a
# Sovereign Weather Station. Idempotent: safe to run twice.
#
#   sudo ./setup.sh
#
# Every change this makes is listed in CHANGES.md. Nothing else is touched.
set -euo pipefail
[ "$EUID" -eq 0 ] || { echo "run with sudo"; exit 1; }
HERE="$(cd "$(dirname "$0")" && pwd)"

echo "==> packages"
apt-get update
apt-get install -y --no-install-recommends \
  python3 python3-smbus2 i2c-tools fake-hwclock

echo "==> files -> /opt/sws"
install -d /opt/sws/station /opt/sws/bin /data
install -m 0644 "$HERE"/station/*.py /opt/sws/station/
install -m 0755 "$HERE"/bin/sws-check "$HERE"/bin/sws-firstboot /opt/sws/bin/
ln -sf /opt/sws/bin/sws-check /usr/local/bin/sws-check

echo "==> real time clock"
# No network means no NTP. Without this, every boot starts in 1970 and the
# whole six months of timestamps are worthless.
if [ -e /dev/rtc0 ] || grep -q ds3231 /proc/devices 2>/dev/null; then
  echo "    hardware RTC present"
else
  echo "    no hardware RTC: falling back to fake-hwclock (drifts, but monotonic)"
  echo "    fit a DS3231 on the same I2C bus if you want real timestamps"
fi
systemctl enable fake-hwclock.service || true

echo "==> services"
install -m 0644 "$HERE"/systemd/*.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable sws-firstboot.service station.service

echo "==> done. reboot, then run: sws-check"
