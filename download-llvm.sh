#!/usr/bin/env bash

set -xue -o pipefail

# llvmorg-19.1.5
COMMIT_SHA=ab4b5a2db582958af1ee308a790cfdb42bd24720
URL="https://github.com/llvm/llvm-project/archive/${COMMIT_SHA}.tar.gz"
TARBALL="${COMMIT_SHA}.tar.gz"
TARBALL_SHA256=da6ac0897bd4fcb509592d36236ddc9d5625fc018d4917f19aeb3ccf8bb6f83b
if [[ "$(uname -s)" == "Darwin" ]]; then
  sha256sum() {
    shasum --algorithm 256 "$@"
  }
fi

if ! [[ -f "${TARBALL}" ]]; then
  wget --quiet ${URL}
fi
echo "${TARBALL_SHA256}  ${TARBALL}" | sha256sum --check
tar -xf "${TARBALL}"
rm ${TARBALL}
mv "llvm-project-${COMMIT_SHA}" llvm-project
patch -d llvm-project -p1 < lldb.patch

CONAN_PROVIDER_COMMIT_SHA=82284c0204e87f36c7d5706bf2963bae735904a4
wget https://raw.githubusercontent.com/conan-io/cmake-conan/${CONAN_PROVIDER_COMMIT_SHA}/conan_provider.cmake \
  -O llvm-project/llvm/conan_provider.cmake

cp -r conanfile.txt llvm-project/llvm
