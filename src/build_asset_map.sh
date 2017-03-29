#!/bin/bash
out=$1
shift
in="$@"
rm -f $out

for f in $in; do
  hash=$(sha256sum $f | cut -c 1-12)
  name=$(basename $f)
  version_name=$(echo $name | sed "s@\\([a-zA-Z]*\\)\\.\\([a-zA-Z]*\\)@\\1-${hash}.\\2@")
  echo "${f#.build/static/}: /assets$(dirname ${f#.build/static})/${version_name}" >> $out
done;
