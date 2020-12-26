# exit script on any error
trap 'exit' ERR

VERSION="0.11.0"

#https://github.com/restic/restic/releases/download/v0.11.0/restic_0.11.0_windows_amd64.zip

FILE_LINUX="restic_${VERSION}_linux_amd64"
FILE_MACOS="restic_${VERSION}_darwin_amd64"
FILE_WINDO="restic_${VERSION}_windows_amd64"

ARCHIVE_LINUX="${FILE_LINUX}.bz2"
ARCHIVE_MACOS="${FILE_MACOS}.bz2"
ARCHIVE_WINDO="${FILE_WINDO}.zip"

URL_DL="https://github.com/restic/restic/releases/download"
URL_LINUX="${URL_DL}/v${VERSION}/${ARCHIVE_LINUX}"
URL_MACOS="${URL_DL}/v${VERSION}/${ARCHIVE_MACOS}"
URL_WINDO="${URL_DL}/v${VERSION}/${ARCHIVE_WINDO}"

DIR_TEMP="bin"
mkdir -p "${DIR_TEMP}"
cd "${DIR_TEMP}"

if [[ ! -f "${FILE_LINUX}" ]]; then
  curl -L --output "${ARCHIVE_LINUX}" "${URL_LINUX}"
  bzip2 --decompress "${ARCHIVE_LINUX}"
fi
if [[ ! -f "${FILE_MACOS}" ]]; then
  curl -L --output "${ARCHIVE_MACOS}" "${URL_MACOS}"
  bzip2 --decompress "${ARCHIVE_MACOS}"
fi
if [[ ! -f "${FILE_WINDO}" ]]; then
  curl -L --output "${ARCHIVE_WINDO}" "${URL_WINDO}"
  unzip -q "${ARCHIVE_WINDO}"
  rm "${ARCHIVE_WINDO}"
fi

chmod u+x *

cd ..


