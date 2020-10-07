#!/bin/bash

echo @@@@@@
env

./.local/bin/update.sh
exec ./.local/bin/jupyter notebook --ip 0.0.0.0

