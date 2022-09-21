
import datetime
WATCH_TIME_MINUTES=30

def getTimeKSTFromTimeStamp(timestamp):
    from datetime import timezone
    utctime = datetime.datetime.now(timezone.utc).strftime("%Y%m%d_%H:%M:%S")
    kstime = datetime.datetime.now().strftime("%Y%m%d_%H:%M:%S")

    # .strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    if utctime == kstime:
        return datetime.datetime.fromtimestamp(timestamp) + datetime.timedelta(hours=9)
    else:
        return datetime.datetime.fromtimestamp(timestamp)

watchStart = getTimeKSTFromTimeStamp(datetime.datetime.now().timestamp())
watchEnd = getTimeKSTFromTimeStamp((datetime.datetime.now() + datetime.timedelta(minutes=WATCH_TIME_MINUTES)).timestamp())

print(watchStart, watchEnd)

print(getTimeKSTFromTimeStamp(datetime.datetime.now().timestamp()).second)