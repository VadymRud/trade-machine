#!/usr/bin/env bash

#parameters
virtualenv_dir=env

# bower for frontend libs
npm install -g bower

# install virtual env
pip3 install virtualenv
# create new env
virtualenv $virtualenv_dir
# activate env
source $virtualenv_dir/bin/activate
# install requirement packages
pip3 install -r "requirements.txt"

# install all bower dependencies
bower install
