#!/usr/bin/python3

from requests import get
from os import system, path
import logging
import time
import json

logger = logging.getLogger(__name__)
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
    configFile = {"auto": "true", "url": "https://raw.githubusercontent.com/ChickenDevs/webcast/main/test-off.xml", "resolution": "1280x720",
                  "videoDelay": 0,"audioDelay": 1, "volume": 0, "preset": "veryfast"}
    out = json.dumps(configFile)
    f = open(f"/etc/webcast/webcast.conf", "w").write(out)

with open(f"/etc/webcast/webcast.conf") as f:
    config = json.load(f)

if config['auto'] == "true":
    # Get the Config file from the Church
    xml = get(config['url']).text
    logger.info("Successfully retrieved XML file")

    # Video Bitrate
    _, videobitrate = xml.split("<video>")
    videobitrate, _ = videobitrate.split("</video>")
    _, videobitrate = videobitrate.split("<custom_bitrate>")
    videobitrate, _ = videobitrate.split("</custom_bitrate>")
    videobitrate = int(videobitrate)
    logger.info(f"Video Bitrate: {videobitrate}")

    # Audio Bitrate
    _, audiobitrate = xml.split("<audio>")
    audiobitrate, _ = audiobitrate.split("</audio>")
    _, audiobitrate = audiobitrate.split("<custom_bitrate>")
    audiobitrate, _ = audiobitrate.split("</custom_bitrate>")
    audiobitrate = int(audiobitrate)
    logger.info(f"Audio Bitrate: {audiobitrate}")

    # RTMP URL
    _, url = xml.split("<url>")
    url, _ = url.split("</url>")
    logger.info(f"RTMP URL: {url}")

    # Stream Password
    _, streamkey = xml.split("<stream>")
    streamkey, _ = streamkey.split("</stream>")
    logger.info(f"RMTP Key: {streamkey}")
else:
    videobitrate = config['vbitrate']
    logger.info(f"Video Bitrate: {videobitrate}")
    
    audiobitrate = config['abitrate']
    logger.info(f"Audio Bitrate: {audiobitrate}")

    url = config['rtmpurl']
    logger.info(f"RTMP URL: {url}")

    streamkey = config['rtmpkey']
    logger.info(f"RMTP Key: {streamkey}")

if url.startswith("rtmp"):  # A stream should be active
    shouldberunning = True
    logger.info("Found Stream URL")
else:
    shouldberunning = False
    logger.info("No Current Stream URL Found")

if system("ps -e | grep ffmpeg") == 0:  # ffmpeg is running
    running = True
    logger.info("ffmpeg running")
else:
    running = False
    logger.info("ffmpeg not running")

if shouldberunning and running:
    logger.info("ffmpeg is already streaming")  # Stream is running

if shouldberunning and not running:
    logger.info("Attemping to start ffmpeg")
    system(f"ffmpeg -hide_banner -f v4l2 -thread_queue_size 16 -framerate 25 "
           f"-video_size {config['resolution']} -input_format mjpeg -i /dev/video0 "
           f"-f alsa -thread_queue_size 1024 -itsoffset {config['audioDelay']} -i sysdefault:CARD=Device "
           "-map 0:v -map 1:a -vcodec h264 -acodec aac "
           f"-ar {audiobitrate} -ac 2 -preset {config['preset']} -b:v {videobitrate} -framerate 25 -g 50 "
           f"-filter:a volume={config['volume']}dB -f flv '{url}/{streamkey}' &")
    time.sleep(5)
    if system("ps -e | grep ffmpeg") == 0:  # ffmpeg is running
        logger.info("Successfully started ffmpeg")
    else:
        logger.error("Could not start ffmpeg")

if running and not shouldberunning:
    logger.info("Attempting to kill ffmpeg")
    system("pkill ffmpeg")  # Kill ffmpeg
    logger.info("Successfully killed ffmpeg")

if not running and not shouldberunning:
    logger.info("No current stream found")  # Stream isn't running
