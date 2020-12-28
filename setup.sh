#!/bin/bash
sudo cp code/webcast.* /etc/systemd/system
sudo cp -r code/webcast /etc
sudo cp -r code/webcastconfig /usr/share/cockpit
sudo systemctl daemon-reload
sudo systemctl enable webcast.timer
