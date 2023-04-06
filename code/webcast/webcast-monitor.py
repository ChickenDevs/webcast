#!/usr/bin/python3
import datetime
import os

output = os.popen('sudo systemctl status webcast.timer').read()
output = output.split('\n')
output = [x for x in output if 'Active:' in x][0]
output = output.split()
dead_since = datetime.datetime.strptime(f'{output[5]} {output[6]}', '%Y-%m-%d %H:%M:%S')

print(f"Webcast has been {output[1]} since {dead_since}")

if datetime.datetime.utcnow() > dead_since + datetime.timedelta(hours=1) and output[1] == 'inactive':
    print("Restarting timer.")
    os.system("sudo systemctl start webcast.timer")
