#!/bin/bash

OUT_DIR="tmp"

if [ -e ./$OUT_DIR ] ; then
  echo "Error: output directory already exists: ./$OUT_DIR"
  exit
fi

################################### TEST 1
mkdir tmp
python Driver1.py -i "test/1/mvspec.xml" -o "tmp/test1.data" -s 5000 -n 100
python Driver2.py -1 "test/1/mvspec.xml" -2 "test/1/dataspec.xml" -i "tmp/test1.data" -o "tmp/out"
cd tmp
hashdeep -rlc md5 out > out.hash
cd ..
if [ -z "$(diff -I '#.*' 'tmp/out.hash' 'test/1/out.hash')" ] ; then
  # If the diff command produces no string output...
  echo "TEST: success"
else
  # If the diff command produces string output...
  echo "TEST: failure"
fi
rm -rf tmp
###################################
