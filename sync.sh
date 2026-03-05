#!/bin/bash
# this is used instead of git cloning lmao
rsync -avz --progress \
  --exclude '__pycache__' \
  /Users/betich/code/work/betich/mini-home-displays/ \
  rpi:code/display/