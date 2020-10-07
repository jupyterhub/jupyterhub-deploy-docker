#!/bin/bash

# Update the git repos

echo Updating FoCS content

cd /home/`whoami`
eval `opam env`

rm -rf focs-notebooks
git clone https://github.com/ocamllabs/focs-notebooks.git
chmod -R 444 focs-notebooks/*
chmod a-w focs-notebooks

