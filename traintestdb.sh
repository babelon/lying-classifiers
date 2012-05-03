#!/bin/sh

dir="dbyank"
rm -r $dir
mkdir $dir
mkdir ./$dir/restaurant
mkdir ./$dir/song
mkdir ./$dir/movie
mkdir ./$dir/other_food

./dbyank.py $dir
./traintest.py $dir -k 2 -n 1 -p 2 -o currentvecs
