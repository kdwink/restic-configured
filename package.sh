#==============================================================================
#
# Package these scripts and restic executable for distribution on remote
# machines.
#
#==============================================================================
# exit script on any error
trap 'exit' ERR

#----------------------------------------------------------------
# increment version
#----------------------------------------------------------------

VERSION_FILE="src/restic/version.txt"
HASH=$(git rev-parse --short HEAD)

OLD_VER=$(grep version ${VERSION_FILE} | cut -d "=" -f2)
NEW_VER=$(( OLD_VER + 1 ))

printf "\n"
printf "OLD_VER: %s \n" "${OLD_VER}"
printf "NEW_VER: %s \n" "${NEW_VER}"
printf "\n"

sed -i '' "s/version=${OLD_VER}\$/version=${NEW_VER}/g" "${VERSION_FILE}"
sed -i '' "s/hash=.*\$/hash=$HASH/g" ${VERSION_FILE}


git commit --all --message "VERSION: ${NEW_VER}"
git tag "v${NEW_VER}"
git push --tags origin HEAD

#----------------------------------------------------------------
# download the binary distribution of restic
#----------------------------------------------------------------
./download-restic-executable.sh


#----------------------------------------------------------------
# package src
#----------------------------------------------------------------
if [[ "$OSTYPE" == "darwin"* ]]; then
    TAR="gtar"
else
    TAR="tar"
fi

TAR_FILE="restic-backup-v${NEW_VER}.tar"

${TAR} --transform 's+^+restic-backup/+' --create --file "${TAR_FILE}" src
${TAR} --transform 's+^+restic-backup/+' --append --file "${TAR_FILE}" config
${TAR} --transform 's+^+restic-backup/+' --append --file "${TAR_FILE}" bin

printf "Created %s \n" "${TAR_FILE}"