#!/bin/sh
set -ex

PYI_PATH=$(python -c "import PyInstaller as _; print(_.__path__[0])")
PYI_RTH_PKGUTIL=$PYI_PATH/hooks/rthooks/pyi_rth_pkgutil.py
patch $PYI_RTH_PKGUTIL < ./pyi_rth_pkgutil.py.patch
