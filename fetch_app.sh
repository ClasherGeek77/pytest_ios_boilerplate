#!/bin/bash
# downloads the app under test from the mobile_app_mock release, so nobody has
# to compile it: the iOS simulator build (Runner.app, x86_64)
# files land in apps/ (git-ignored) and are checked against the release SHA256SUMS.txt
#   ./fetch_app.sh                    the pinned release
#   APP_VERSION=v1.0.0 ./fetch_app.sh pick another release tag
set -e
cd "$(dirname "$0")"

VERSION="${APP_VERSION:-v1.0.0}"
BASE="https://github.com/ClasherGeek77/mobile_app_mock/releases/download/$VERSION"
mkdir -p apps
if [ -t 1 ]; then BAR=--progress-bar; else BAR=-sS; fi

sha256() {
    if command -v shasum > /dev/null; then shasum -a 256 "$@"; else sha256sum "$@"; fi
}

curl -fsSL "$BASE/SHA256SUMS.txt" -o apps/SHA256SUMS.txt

for FILE in "ted_mobile_app_test-$VERSION-ios-simulator.zip"; do
    if [ ! -f "apps/$FILE" ]; then
        echo "downloading $FILE"
        curl -fL $BAR "$BASE/$FILE" -o "apps/$FILE"
    fi
    EXPECTED=$(grep -F " $FILE" apps/SHA256SUMS.txt | cut -d' ' -f1)
    ACTUAL=$(sha256 "apps/$FILE" | cut -d' ' -f1)
    if [ -z "$EXPECTED" ] || [ "$EXPECTED" != "$ACTUAL" ]; then
        echo "checksum mismatch for apps/$FILE, deleting it, run this script again"
        rm -f "apps/$FILE"
        exit 1
    fi
    echo "ok  $FILE"
done

if [ ! -d apps/Runner.app ]; then
    unzip -q -o "apps/$FILE" -d apps
fi

echo "app ready in apps/"
