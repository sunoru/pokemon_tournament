#!/bin/sh
set -ex

cd `dirname $(realpath $0)`/..
pyinstaller ./pmtour.spec -y --debug all
cp ./README.md ./dist/pmtour
