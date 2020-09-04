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
sed -i ''q "s/hash=.*\$/hash=$HASH/g" ${VERSION_FILE}


git commit --all --message "VERSION: ${NEW_VER}"
git push origin HEAD


#----------------------------------------------------------------
# package src
#----------------------------------------------------------------

tar --create --verbose --gzip --file restic-backup-v${NEW_VER}.tgz src