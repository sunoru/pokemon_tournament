#!/bin/bash
set -ex

cd ..
pyinstaller ./pmtour.spec
cd dist
cp ../README.md ./pmtour
if [ "$RUNNER_OS" == "Windows" ]; then
    7z a -r ./pmtour.zip ./pmtour
else
    zip -r ./pmtour.zip ./pmtour
fi
