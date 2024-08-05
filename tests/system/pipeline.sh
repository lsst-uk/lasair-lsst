#!/bin/sh

cd ../../deploy
ansible-playbook ../tests/system/pipeline.yaml

