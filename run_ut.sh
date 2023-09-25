#!/bin/bash
echo 'run unit tests'
cmd=executing python -m unittest discover -s unittest/ -p 'test_*.py'
echo $cmd
eval $cmd