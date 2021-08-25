#!/bin/bash

scriptloc=$(dirname "$0");
currdir=$(pwd);

export PATH="$scriptloc/bin":$PATH
export PYTHONPATH="$scriptloc/":"$scriptloc"/develop:$PYTHONPATH

cd "$scriptloc"

if [ ! -d "develop" ]; then
    echo "MKDIR"
    mkdir "develop"
fi


if [ ! "$(ls -A develop)" ]; then
    "python" "setup.py" "develop" --install-dir "develop"
fi

cd "$currdir"
