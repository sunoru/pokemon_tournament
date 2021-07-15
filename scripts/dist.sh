#!/bin/sh
set -ex

cd ..
pyinstaller ./pmtour.spec -y --debug all
cp ./README.md ./dist/pmtour
zip ./dist/pmtour.zip ./dist/pmtour -r
