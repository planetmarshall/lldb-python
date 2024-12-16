#!/usr/bin/env bash

set -eux -o pipefail

INSTALL_DIR=$(realpath "${1:-/usr/local/bin}")
CCACHE_VERSION=4.10.2
CCACHE_BASENAME=ccache-${CCACHE_VERSION}-linux-x86_64
CCACHE_TARBALL=${CCACHE_BASENAME}.tar.xz
CCACHE_SHA256=80cab87bd510eca796467aee8e663c398239e0df1c4800a0b5dff11dca0b4f18
CCACHE_URL=https://github.com/ccache/ccache/releases/download/v${CCACHE_VERSION}/${CCACHE_TARBALL}
pushd /tmp || exit
wget --quiet ${CCACHE_URL}
echo "${CCACHE_SHA256}  ${CCACHE_TARBALL}" | sha256sum --check
tar -xf ${CCACHE_TARBALL}
mv ${CCACHE_BASENAME}/ccache "${INSTALL_DIR}"
rm -rf ${CCACHE_BASENAME}
popd
