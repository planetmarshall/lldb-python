#!/usr/bin/env bash

set -xue -o pipefail

COMMIT_SHA=ea3d0db130b9a6c4678c11dd8bc48e5630624b62
URL=https://github.com/llvm/llvm-project/archive/${COMMIT_SHA}.tar.gz
TARBALL="${COMMIT_SHA}.tar.gz"
TARBALL_SHA256=61885612507cd439d0d08305ff6c2a60cf0923e7b046ea3a447f1b78d92de957
if [[ "$(uname -s)" == "Darwin" ]]; then
  shasum256() {
    shasum --algorithm 256 "$@"
  }
fi

if ! [[ -f "${TARBALL}" ]]; then
  wget --quiet ${URL}
fi
echo "${TARBALL_SHA256}  ${TARBALL}" | shasum256 --check
tar -xf "${TARBALL}"
rm ${TARBALL}
mv "llvm-project-${COMMIT_SHA}" llvm-project
