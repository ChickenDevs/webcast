#!/bin/bash
sudo cp code/webcast.* /etc/systemd/system
sudo cp -r code/webcast /etc
sudo chown -R webcast:webcast /etc/webcast
chmod 664 /etc/webcast/webcast.conf
chmod 775 /etc/webcast/webcast.py
sudo cp -r code/webcastconfig /usr/share/cockpit
sudo systemctl daemon-reload
sudo systemctl enable webcast.timer
