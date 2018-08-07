#!/bin/sh


# recursively removes all .pyc files 
find . -name "*.pyc" -exec rm -f {} \;
