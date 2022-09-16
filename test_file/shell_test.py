import os
import subprocess
import json
from csv import DictWriter
import datetime


class ShellLog:
    def __init__(self, data):
        self.data = data
        self.parseKey = ['detected_protocol_name',
                         'host_server_name',
                         'dns_host_name',
                         'local_ip',
                         'other_ip',
                         'local_port',
                         'other_port',
                         'first_seen_at',
                         'first_update_at',
                         'last_seen_at',
                         'spend_time']

        self.resultData = {}

    def isWg0Format(self):
        if 'interface' in self.data.keys():
            if self.data['interface'] == "wg0":
                return True
        return False

    def parseData(self):
        self.data = self.data['flow']
        for key in self.parseKey:
            try:
                if key.split('_')[-1] == "at":
                    self.resultData[key] = self.getTimeKSTFromTimeStamp(int(self.data[key]) / 1000)
                else:
                    self.resultData[key] = self.data[key]

            except Exception as e:
                self.resultData[key] = 'NULL'

    def calcSpendTime(self):
        print(self.resultData['last_seen_at'], self.resultData['first_seen_at'])
        self.resultData['spend_time'] = self.resultData['last_seen_at'] - self.resultData['first_seen_at']

    def reformatTime(self):
        self.resultData['first_seen_at'] = self.resultData['first_seen_at'].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        self.resultData['first_update_at'] = self.resultData['first_update_at'].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        self.resultData['last_seen_at'] = self.resultData['last_seen_at'].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        self.resultData['spend_time'] = self.resultData['spend_time'].total_seconds()

    def hasLocalIP(self):
        if self.resultData['local_ip'] != 'NULL':
            return True
        else:
            return False

    def getTimeKSTFromTimeStamp(self, timestamp):
        from datetime import timezone
        utctime = datetime.datetime.now(timezone.utc).strftime("%Y%m%d_%H:%M:%S")
        ostime = datetime.datetime.now().strftime("%Y%m%d_%H:%M:%S")

        # .strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        if utctime == ostime:
            return datetime.datetime.fromtimestamp(timestamp) + datetime.timedelta(hours=9)
        else:
            return datetime.datetime.fromtimestamp(timestamp)

    def getHost_server_nameAndOther_ip(self):
        return self.resultData['host_server_name'], self.resultData['other_ip']

    def getLocalIP(self):
        return self.resultData['local_ip']

    def getLastSeenAtDatetime(self):
        if type(self.resultData['last_seen_at']) == datetime.datetime:
            return self.resultData['last_seen_at']
        elif type(self.resultData['last_seen_at']) == str:
            return datetime.datetime.strptime(self.resultData['last_seen_at'], '%Y-%m-%d %H:%M:%S.%f')

    def getFilename(self):
        return f"./csv/{self.resultData['local_ip']}.csv"

    def save(self):
        with open(self.getFilename(), 'a', newline='') as f_object:
            dictwriter_object = DictWriter(f_object, fieldnames=self.parseKey)
            if os.path.getsize(self.getFilename()) == 0:
                dictwriter_object.writeheader()
            dictwriter_object.writerow(self.resultData)
            f_object.close()

    def __str__(self):
        return f"{self.resultData}"


class PacketWatchDog:
    # 30분 이내 2개 이상의 패킷만 저장.
    # duration = 마지막 패킷 시간 - 처음 패킷 시간
    # 필터링 조건 :  IP or DNS
    # CSV columns: date, host_server_name, other_ip, duration
    # 파일명 local_ip.csv
    # 날짜 변경을 기준으로 짜르기

    def __init__(self, local_ip):
        self.local_ip = local_ip
        self.MIN_WATCH_COUNT = 2
        self.WATCH_TIME_MINUTES = 30
        self.DESTINATION_FILTER = ['IP', 'DNS', 'others....']
        self.CSV_COLUMNS = ['date', 'host_server_name', 'other_ip', 'duration']
        self.FILENAME = f"./csv/duration/{self.local_ip}.csv"

        self.host_server_name = 'NULL'
        self.other_ip = 'NULL'

        self.watchStart = datetime.datetime.now()
        self.watchEnd = datetime.datetime.now() + datetime.timedelta(minutes=self.WATCH_TIME_MINUTES)
        self.packetTimeList = []

    def addPacket(self, host_server_name, other_ip, packetTime):
        self.host_server_name = host_server_name
        self.other_ip = other_ip
        appendedPacketTime = packetTime
        self.packetTimeList.append(appendedPacketTime)

    def calcDuration(self):
        if self.isTimeToSave():
            return self.packetTimeList[-1] - self.watchStart

    def isTimeToSave(self):
        if self.watchEnd < datetime.datetime.now():
            return True
        else:
            return False

    def isSaveCondition(self):
        if len(self.packetTimeList) >= self.MIN_WATCH_COUNT:
            return True
        else:
            return False

    def getDataForSave(self):
        return {'date': self.watchStart.strftime('%Y-%m-%d')[:-3],
                'host_server_name': self.host_server_name,
                'other_ip': self.other_ip,
                'duration': self.calcDuration().total_seconds()}

    def isEndofDay(self):
        if datetime.datetime.now().hour == '23' and datetime.datetime.now().minute == '59' and datetime.datetime.now().second == '59':
            return True
        else:
            return False

    def save(self):
        if self.isSaveCondition():
            with open(self.FILENAME, 'a', newline='') as f_object:
                dictwriter_object = DictWriter(f_object, fieldnames=self.CSV_COLUMNS)
                if os.path.getsize(self.FILENAME) == 0:
                    dictwriter_object.writeheader()
                dictwriter_object.writerow(self.getDataForSave())
                f_object.close()


if __name__ == "__main__":
    proc = subprocess.Popen(['./json_capture.sh'], stdout=subprocess.PIPE)

    activeWatchDog = {}
    while True:
        line = proc.stdout.readline().decode('utf-8').strip()
        if not line: break
        try:
            line = dict(json.loads(line))

            # Save packet data
            shelllog = ShellLog(line)
            if shelllog.isWg0Format():
                shelllog.parseData()
                shelllog.calcSpendTime()
                shelllog.reformatTime()
                print(shelllog)

                if shelllog.hasLocalIP():
                    shelllog.save()

            # Packet WatchDog
            if shelllog.getLocalIP() not in activeWatchDog:
                activeWatchDog[shelllog.getLocalIP()] = PacketWatchDog(shelllog.getLocalIP())

            activeWatchDog[shelllog.getLocalIP()].addPacket(*shelllog.getHost_server_nameAndOther_ip(),
                                                      shelllog.getLastSeenAtDatetime())

            if activeWatchDog[shelllog.getLocalIP()].isTimeToSave() or activeWatchDog[shelllog.getLocalIP()].isEndofDay():
                activeWatchDog[shelllog.getLocalIP()].save()
                del activeWatchDog[shelllog.getLocalIP()]

        except Exception as e:
            print(e)
