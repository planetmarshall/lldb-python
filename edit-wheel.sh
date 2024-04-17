#!/usr/bin/env bash
#
# Removes the lib folder installed by LLDB and moves
# things around to sensible locations
set -e -o pipefail

WHEEL_PATH=$1
WORKING_DIR=$(dirname "${WHEEL_PATH}")
WHEEL=$(basename "${WHEEL_PATH}")
pushd "${WORKING_DIR}"
wheel unpack "${WHEEL}"
rm ${WHEEL}

WHEEL_DIR=$(find . -maxdepth 1 -name 'lldb_unofficial*' -type d)
[[ -z "${WHEEL_DIR}" ]] && echo "WHEEL_DIR was null" && exit 1
pushd "${WHEEL_DIR}"

DATA_DIR=$(find . -name data -type d)
[[ -z "${DATA_DIR}" ]] && echo "DATA_DIR was null" && exit 1

# remove the extra libs installed by LLVM. These are usually symlinks but they
# are converted into files in the wheel. We can't just not install them in the first
# place as LLVM uses them to create the _lldb python library which we need.
echo "Removing unused library files"
rm ${DATA_DIR:?}/lib/liblldb*

SITE_PACKAGES=$(find . -name site-packages -type d)
[[ -z "${SITE_PACKAGES}" ]] && echo "SITE_PACKAGES was null" && exit 1

# the lldb libraries expect to find lldb-server at ../bin/lldb-server
# we could use LLDB_DEBUGSERVER_PATH but it's preferable to not have to define environment variables
echo "Moving lldb-server"
mv "${DATA_DIR:?}/bin" "${SITE_PACKAGES}"

# Fixup the paths in the record file
echo "Fixing up the RECORD file"
RECORD_FILE=$(find . -name RECORD)
[[ -z "${RECORD_FILE}" ]] && echo "RECORD_FILE was null" && exit 1
sed -i.bak '/liblldb/d' "${RECORD_FILE}"

LLDB_SERVER_PATH=$(find * -name lldb-server)

echo ${LLDB_SERVER_PATH}
sed -i.bak "s|^.*lldb-server|${LLDB_SERVER_PATH}|" ${RECORD_FILE}

popd
wheel pack "${WHEEL_DIR}"
rm -r "${WHEEL_DIR}"

popd
