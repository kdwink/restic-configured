# exit script on any error
trap 'exit' ERR

export PYTHONPATH="../src/"

cd test

python3 -m unittest discover --pattern '*.py'
