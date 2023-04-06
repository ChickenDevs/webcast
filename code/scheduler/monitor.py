#!/usr/bin/python3
import datetime
import json

import googleapiclient.discovery
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

from smtplib import SMTP_SSL
from email.message import EmailMessage

NOW = datetime.datetime.now(tz=datetime.timezone.utc)
with open('/opt/webcast/recurring.json') as f:
    RECURRING = json.load(f)


def convert_time(time: str):
    if not time:
        return ''

    return datetime.datetime.fromisoformat(time.replace('Z', '-00:00'))

stream_ids = {
    "wardname": "STREAM_ID_FROM_GOOGLE_API"
}

for ward in stream_ids.keys():
    creds = Credentials.from_authorized_user_file(f'/opt/webcast/auth/{ward}.json')
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

    broadcasts = youtube.liveBroadcasts().list(
        part="id,snippet,contentDetails,status",
        mine=True,
        maxResults=50
    ).execute()

    for broadcast in broadcasts['items']:
        if not broadcast['snippet'].get('scheduledStartTime', None):
            youtube.liveBroadcasts().delete(id=broadcast['id']).execute()
            continue

        endTime = convert_time(broadcast['snippet'].get('scheduledEndTime', ''))
        if not endTime:
            endTime = convert_time(broadcast['snippet']['scheduledStartTime']) + datetime.timedelta(hours=1)

        if NOW > endTime and broadcast['status']['lifeCycleStatus'] != 'complete':
            stream_id = stream_ids.get(ward, None)
            stream = youtube.liveStreams().list(
                part="id,status",
                id=stream_id
            ).execute()['items'][0]
            if (stream['status']['streamStatus'] == 'inactive') or (NOW > endTime + datetime.timedelta(minutes=15)):
                youtube.liveBroadcasts().transition(part='id', id=broadcast['id'], broadcastStatus='complete').execute()
                print(f"Marked broadcast for {ward} complete ({broadcast['id']})")
                print(f"Reason: ", end='')
                print(f"Stream status ({stream['status']['streamStatus']})" if stream['status']['streamStatus'] == 'inactive' else "Time exceeded 15 minutes past end time")

        if broadcast['status']['lifeCycleStatus'] == 'complete' and datetime.datetime.now().day != endTime.day:
            with open('/opt/webcast/clerk_emails.json') as f:
                clerks = json.load(f)
            viewers = round(int(youtube.videos().list(part='statistics', id=broadcast['id']).execute()['items'][0]['statistics']['viewCount']) * 2.1)
            msg = EmailMessage()
            msg["Subject"] = "Online YouTube Meeting Attendance"
            msg["From"] = "Webcast <TheEmailYouSendFrom@gmail.com>"
            msg["To"] = clerks[ward]
            msg.set_content(f"The number of individuals watching {broadcast['snippet']['title']} online on {convert_time(broadcast['snippet']['scheduledStartTime']).strftime('%d %b %Y')} was {viewers}.\n\n\nThis is an automated message. Please do not respond.")
            with SMTP_SSL('SMTP_SERVER_HERE', 465) as smtp:
                smtp.login('TheEmailYouSendFrom@gmail.com', 'ITS_PASSWORD')
                smtp.send_message(msg)
                smtp.quit()
            youtube.liveBroadcasts().delete(id=broadcast['id']).execute()
            print(f"Deleted broadcast on {ward} ({broadcast['id']})")

        if broadcast['contentDetails'].get("boundStreamId", "") != stream_ids.get(ward, "NOT FOUND"):
            youtube.liveBroadcasts().bind(
                id=broadcast['id'],
                part="id",
                streamId=stream_ids.get(ward, '')
            ).execute()
            print(f"Attempted to bind stream to broadcast for {ward}")

    for event in RECURRING[ward]:
        changeInDays = event['day'] - datetime.datetime.now().weekday()
        if changeInDays < 0:
            changeInDays += 7
        recurringDate = datetime.datetime.now() + datetime.timedelta(days=changeInDays)
        startTime = datetime.datetime.combine(recurringDate, datetime.time(*[int(x) for x in event['start'].split(':')]))
        endTime = datetime.datetime.combine(recurringDate, datetime.time(*[int(x) for x in event['end'].split(':')]))
        startTime = startTime.replace(tzinfo=NOW.astimezone().tzinfo)
        endTime = endTime.replace(tzinfo=NOW.astimezone().tzinfo)

        if startTime not in [convert_time(x['snippet']['scheduledStartTime']) for x in broadcasts['items']] and startTime > NOW:
            new = youtube.liveBroadcasts().insert(
                part='id,snippet,contentDetails,status',
                body={
                    'snippet': {
                        'title': event['title'],
                        'scheduledStartTime': startTime.isoformat(),
                        'scheduledEndTime': endTime.isoformat(),
                    },
                    'contentDetails': {
                        'enableAutoStart': 'true',
                    },
                    'status': {
                        'privacyStatus': 'public',
                        'selfDeclaredMadeForKids': 'true',
                    },
                }
            ).execute()
            youtube.liveBroadcasts().bind(
                id=new['id'],
                part="id",
                streamId=stream_ids.get(ward, '')
            ).execute()

