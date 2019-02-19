#!/bin/bash

if [ -f ~/cloudbolt-8.0.box ]; then
        rm ~/cloudbolt-8.0.box
fi
vagrant package --base cloudbolt --output=~/cloudbolt-8.0.box
vagrant box add ~/cloudbolt-8.0.box --name cloudbolt-8.0 --force
