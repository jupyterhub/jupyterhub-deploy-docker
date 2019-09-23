#!/bin/bash

# Update the git repos

echo update

cd /home/`whoami`

rm -rf focs-201920-notebooks
git clone https://github.com/ocamllabs/focs-201920-notebooks.git
git clone https://github.com/jonludlam/focs-support.git
cd focs-support
dune build
dune install

