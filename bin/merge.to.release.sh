#!/bin/sh

./bin/run.command.py 'git checkout release'
./bin/run.command.py 'git merge master'
./bin/run.command.py 'git push'
./bin/run.command.py 'git checkout master'
./bin/run.command.py 'git pull'

