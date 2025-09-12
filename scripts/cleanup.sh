#!/bin/bash

firstname=$1
surname=$2
email=$3

set -e

find . -type f | while IFS= read -r line; do 
	sed -i "s/Jerry/$firstname/g" $line; 
	sed -i "s/jsnitsel/$email/g" $line;
	sed -i "s/Snitselaar/$surname/g" $line;
done
