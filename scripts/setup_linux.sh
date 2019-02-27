#!/usr/bin/env bash
set -x

sudo apt-get update
sudo apt-get install -y python3.5 python3.5-dev python3-pip libgtk2.0-dev libgtk-3-dev libjpeg-dev libtiff-dev libsdl1.2-dev libgstreamer-plugins-base0.10-dev libnotify-dev freeglut3 freeglut3-dev libsm-dev libwebkitgtk-dev libwebkitgtk-3.0-dev
python3 -m pip install -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-14.04/ wxPython==4.0.4
