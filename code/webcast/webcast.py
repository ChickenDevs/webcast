#!/usr/bin/python3

from requests import get
from requests.exceptions import HTTPError
from os import system, path, sys, popen
from sys import exit
import logging
import datetime
import time
import json
import googleapiclient.discovery
from google.oauth2.credentials import Credentials

stream_ids = {
    "wardname": "STREAM_ID_FROM_GOOGLE_API"
}

logger = logging.getLogger("webcast")
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s: %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Get Config from Cockpit
try:
    path.isfile('/etc/webcast/webcast.conf')
except Exception as err:
    logger.warning("Couldn't find config file, creating file with defaults")
    configFile = {"auto": "true", "url": "https://raw.githubusercontent.com/ChickenDevs/webcast/main/test-off.xml",
                  "resolution": "1280x720", "videoDelay": 0, "audioDelay": 1, "volume": 0, "preset": "veryfast",
                  "shouldbepaused": "false", "wards": ["wardname"]}
    out = json.dumps(configFile)
    f = open(f"/etc/webcast/webcast.conf", "w").write(out)
    f.close()

with open(f"/etc/webcast/webcast.conf") as f:
    config = json.load(f)

endTime = datetime.datetime.now(tz=datetime.timezone.utc)
currently_live = None
ward_yt = None
status = None
shouldberunning = False
shouldbepaused = config['shouldbepaused']
now = datetime.datetime.now(tz=datetime.timezone.utc)

if system("ps -e | grep ffmpeg") == 0:  # ffmpeg is running
    running = True
    if "-loop" in popen("ps -ef | grep ffmpeg").read():
        paused = True
    else:
        paused = False
else:
    running = False
    paused = False
logger.debug(f"Running: {running}")
logger.debug(f"Paused: {paused}")
logger.debug(f"Should be paused: {shouldbepaused}")

if config['auto'] == "true":
    broadcasts = []
    # Check for scheduled broadcast
    for ward in config['wards']:
        try:
            wardname = ward.lower().replace(" ", "")
            creds = Credentials.from_authorized_user_file(f'/etc/webcast/auth/{wardname}.json')
            youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

            request = youtube.liveBroadcasts().list(
                part='snippet,contentDetails,status',
                mine=True,
                maxResults=10
            )
            response = request.execute()
            for broadcast in response['items']:
                start = datetime.datetime.fromisoformat(broadcast['snippet']['scheduledStartTime'].replace('Z', '-00:00'))
                end = broadcast['snippet'].get('scheduledEndTime', None)
                end = datetime.datetime.fromisoformat(end.replace('Z', '-00:00')) if end else start + datetime.timedelta(hours=1)
                broadcasts.append({
                    'ward': wardname,
                    'start': start,
                    'end': end,
                    'status': broadcast['status']['lifeCycleStatus'],
                    'yt': youtube
                })
        except Exception as e:
            raise e
            exit(1)
            continue

    # If broadcast scheduled in next 10 mintues, start now
    for broadcast in broadcasts:
        if (now > broadcast['start'] - datetime.timedelta(minutes=10)) and (now < broadcast['end']) and (broadcast['status'] != 'complete'):
            logger.info(f"Found broadcast for ward {broadcast['ward']} that should be running")
            currently_live = broadcast['ward']
            ward_yt = broadcast['yt']
            shouldberunning = True
            endTime = broadcast['end'] 
            if path.isfile(f'/etc/webcast/rtmp/{broadcast["ward"]}.json'):
                with open(f'/etc/webcast/rtmp/{broadcast["ward"]}.json') as f:
                    rtmp = json.load(f)
                url = rtmp['url']
                key = rtmp['key']
            else:
                logger.warning("Couldn't find RTMP details, retrieving from youtube")
                request = ward_yt.liveStreams().list(
                    part='cdn',
                    id=stream_ids.get(broadcast['ward'], '')
                )
                response = request.execute()

                url = response['items'][0]['cdn']['ingestionInfo']['ingestionAddress']
                key = response['items'][0]['cdn']['ingestionInfo']['streamName']

                out = json.dumps({'url': url, 'key': key})
                with open(f"/etc/webcast/rtmp/{broadcast['ward']}.json", "w") as f:
                    f.write(out)
            break
else:
    shouldberunning = True
    url = config['rtmpurl']
    logger.debug(f"RTMP URL: {url}")

    key = config['rtmpkey']
    logger.debug(f"RMTP Key: {key}")

videobitrate = config['vbitrate']
logger.debug(f"Video Bitrate: {videobitrate}")

audiobitrate = config['abitrate']
logger.debug(f"Audio Bitrate: {audiobitrate}")

if shouldberunning and running:
    if shouldbepaused and not paused:
        logger.info("Switching to paused loop")
        system("pkill ffmpeg")
        system(f"ffmpeg -hide_banner -loop 1 -i /etc/webcast/sacrament.png -f flv '{url}/{key}' &")
    if paused and not shouldbepaused:
        logging.info("Ending paused loop")
        system("pkill ffmpeg")
        running = False

if shouldberunning and not running:
    if shouldbepaused:
        system(f"ffmpeg -hide_banner -loop 1 -i /etc/webcast/sacrament.png -f flv '{url}/{key}' &")
        time.sleep(3)
    else:
        logger.info("Attemping to start ffmpeg")
        system("pkill ffmpeg")
        system(f"ffmpeg -hide_banner -f v4l2 -thread_queue_size 16 -framerate 25 "
               f"-video_size {config['resolution']} -input_format mjpeg -i /dev/video0 "
               f"-f alsa -thread_queue_size 1024 -itsoffset {config['audioDelay']} -i sysdefault:CARD=Device "
               "-map 0:v -map 1:a -vcodec h264 -acodec aac "
               f"-ar {audiobitrate} -ac 2 -preset {config['preset']} -b:v {videobitrate} -framerate 25 -g 50 "
               f"-filter:a volume={config['volume']}dB -f flv '{url}/{key}' &")
        time.sleep(3)
    if system("ps -e | grep ffmpeg") == 0:  # ffmpeg is running
        logger.info("Successfully started ffmpeg")
        running = True
    else:
        logger.error("Could not start ffmpeg")

if running and not shouldberunning:
    if config['auto'] == False:
        data = sorted(
            [[x['end'], now - x['end'], x['status']] for x in broadcasts if now - x['end'] > datetime.timedelta()],
            key=lambda x: x[1]
        )[0]
        endTime = data[0]
        status = data[2]
        logger.info(f"Checking for overtime. Now: {datetime.datetime.now(tz=datetime.timezone.utc)} Endtime: {endTime}")
        if datetime.datetime.now(tz=datetime.timezone.utc) < endTime + datetime.timedelta(minutes=10) and status != "complete":
            logger.info("Past run time, allowing 10 minutes over.")
        else:
            logger.info("Attempting to kill ffmpeg (past 10 minutes)")
            system("pkill ffmpeg")  # Kill ffmpeg
            logger.info("Successfully killed ffmpeg")
    else:
        system("pkill ffmpeg")
        logger.info("Successfully killed ffmpeg")

if not running and not shouldberunning:
    logger.info("No current stream found")  # Stream isn't running

