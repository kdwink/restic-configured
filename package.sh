# exit script on any error
trap 'exit' ERR

#----------------------------------------------------------------
# increment version
#----------------------------------------------------------------

VERSION_FILE="src/restic/version.txt"
HASH=`git rev-parse --short HEAD`

OLD_VER=`grep version ${VERSION_FILE} | cut -d "=" -f2`
NEW_VER=`expr $oldnum + 1`
sed -i "s/version=${OLD_VER}\$/version=${NEW_VER}/g" ${VERSION_FILE}
sed -i "s/hash=.*\$/hash=$HASH/g" ${VERSION_FILE}


git commit -m "VERSION: ${NEW_VER}" -a
git push origin HEAD


#----------------------------------------------------------------
# package src
#----------------------------------------------------------------

tar --create --verbose --gzip --file restic-backup-v${NEW_VER}.tgz