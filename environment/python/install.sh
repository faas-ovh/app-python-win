#!/bin/bash
cd 2.faas.ovh
apt update -y
#apt install python-pip -y
apt install python3-pip -y
pip3 --version
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
ls
