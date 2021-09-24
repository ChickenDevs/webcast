#!/bin/bash
sudo apt install cockpit ffmpeg -y
sudo mkdir /etc/systemd/system/cockpit.socket.d
sudo cat > /etc/systemd/system/cockpit.socket.d/listen.conf << EOF
[Socket]
ListenStream=
ListenStream=443
EOF
sudo systemctl daemon-reload
sudo systemctl restart cockpit.socket
sudo cp code/services/* /etc/systemd/system
sudo cp -r code/webcast /etc
sudo chown -R webcast:webcast /etc/webcast
chmod 644 /etc/webcast/webcast.conf /etc/webcast/webcast.key
chmod 775 /etc/webcast/webcast.py /etc/webcast/webcast-monitor.py
chmod 775 -R /etc/webcast/api
sudo cp -r code/webcastconfig /usr/share/cockpit
sudo systemctl daemon-reload
sudo systemctl enable --now webcast.timer
sudo systemctl enable --now webcast-api.service
sudo systemctl enable --now webcast-monitor.service
