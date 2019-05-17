#!/bin/bash

old=$(pwd)
rsync="rsync -raz --no-o --no-g --info=progress2 --exclude 'log*' --dry-run"
data="/vol/hmi/projects/ruben"
anaconda="$hmi/miniconda"
dest="$hmi/packages"

# [[ ! -d $dest ]] && echo "dir doesn't exist: $dest" && exit 1

# rsync $HOME/irl/irl/exp/confs "$hmi/confs"

packages=("$data/packages/psr" "$data/packages/py-vgdl" "$data/packages/irl" "$data/packages/rubens")

for d in "${packages[@]}"; do
  echo $d
  [[ ! -d $d ]] && continue
  cd $d
  which "$anaconda/bin/python"
  "$anaconda/bin/pip" install --upgrade --no-deps --force-reinstall -e .
  cd ..
done

cd $old
