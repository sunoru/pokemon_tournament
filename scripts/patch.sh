#!/bin/sh
set -ex

PYI_PATH=$(python -c "import PyInstaller as _; print(_.__path__[0])")
PYI_RTH_PKGUTIL=$PYI_PATH/hooks/rthooks/pyi_rth_pkgutil.py
if [ "$RUNNER_OS" == "Windows" ]; then
    unix2dos ./pyi_rth_pkgutil.py.patch
fi
patch $PYI_RTH_PKGUTIL < ./pyi_rth_pkgutil.py.patch
if [ "$RUNNER_OS" == "Windows" ]; then
    dos2unix ./pyi_rth_pkgutil.py.patch
fi
