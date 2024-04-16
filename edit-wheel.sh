#!/usr/bin/env bash
#
# Removes the lib folder installed by LLDB and moves
# things around to sensible locations
set -ue -o pipefail

WHEEL_PATH=$1
WORKING_DIR=$(dirname ${WHEEL_PATH})
WHEEL=$(basename ${WHEEL_PATH})
PATTERN='lldb_unofficial*'
pushd ${WORKING_DIR}
wheel unpack ${WHEEL}

#rm ${WHEEL}
DIR=$(find . -maxdepth 1 -name "${PATTERN}" -type d)
[[ -z "${DIR}" ]] && echo "DIR was null" && exit 1
rm -r ${DIR}/lib

RECORD_FILE=$(find ${DIR} -name RECORD)
sed -i '/lib/d' ${RECORD_FILE}
sed -i 's|site_packages/||' ${RECORD_FILE}
mv ${DIR}/site_packages/* ${DIR}
rm -rf ${DIR}/site_packages

#wheel pack ${DIR}
popd
