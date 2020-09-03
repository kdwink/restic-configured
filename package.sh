# exit script on any error
trap 'exit' ERR

#----------------------------------------------------------------
# increment version
#----------------------------------------------------------------

VERSION_FILE="src/restic/version.txt"
HASH=`git rev-parse --short HEAD`

oldnum=`grep version ${VERSION_FILE} | cut -d "=" -f2`
newnum=`expr $oldnum + 1`
sed -i "s/version=$oldnum\$/version=$newnum/g" ${VERSION_FILE}
sed -i "s/hash=.*\$/hash=$HASH/g" ${VERSION_FILE}


git commit -m "VERSION: $newnum" -a
git push origin HEAD