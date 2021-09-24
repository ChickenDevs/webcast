#!/usr/bin/python3

import json
from os import path, system
import requests

try:
    with open('/etc/webcast/webcast.key') as f:
        old_key = f.read()
except FileNotFoundError:
    old_key = ''

if not path.isfile('/etc/webcast/webcast.conf'):
    exit(1)

with open('/etc/webcast/webcast.conf') as f:
    config = json.load(f)

if config.get('auto', 'false') != 'true':
    exit(1)

url = config.get('url')
xml = requests.get(url).text

_, key = xml.split('<stream>')
key, _ = key.split('</stream>')

if key != old_key:
    system(f'echo {key} > /etc/webcast/webcast.key')
    system('sudo systemctl start webcast.timer')

