#!/bin/sh

set -ex

PANDOC_VER=2.2.1
PANDOC_TGZ=pandoc-${PANDOC_VER}-linux.tar.gz
PARENT_DIR=${1:-.}
PANDOC_BIN=${PARENT_DIR}/pandoc2/bin/pandoc

if [ -x "$PANDOC_BIN" ]; then
    echo "pandoc2 already installed"
    exit 0
fi

cd "$PARENT_DIR"

wget "https://github.com/jgm/pandoc/releases/download/${PANDOC_VER}/${PANDOC_TGZ}" -O "${PANDOC_TGZ}"

tar -xzvf "${PANDOC_TGZ}"

rm -rf pandoc2

mv "pandoc-${PANDOC_VER}" pandoc2

[ -x "$PANDOC_BIN" ] || exit 1
