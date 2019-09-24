#!/bin/bash

# Update the git repos

echo Updating FoCS content

cd /home/`whoami`

rm -rf focs-201920-notebooks
git clone https://github.com/ocamllabs/focs-201920-notebooks.git
chmod -R 666 focs-201920-notebooks/*

pushd /tmp/
rm -rf focs-support
git clone https://github.com/jonludlam/focs-support.git
cd focs-support
dune build
dune install
popd

