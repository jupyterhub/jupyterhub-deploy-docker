#!/bin/bash

/home/opam/.local/bin/update.sh
exec /home/opam/.local/bin/jupyter notebook --ip 0.0.0.0

