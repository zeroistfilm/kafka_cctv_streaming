import os
import subprocess
import json
from csv import DictWriter
import datetime

def getTimeKSTFromTimeStamp(timestamp):
    from datetime import timezone
    utctime = datetime.datetime.now(timezone.utc).strftime("%Y%m%d_%H:%M:%S")
    ostime = datetime.datetime.now().strftime("%Y%m%d_%H:%M:%S")

    if utctime == ostime:
        return (datetime.datetime.fromtimestamp(timestamp) + datetime.timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    else:
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

proc = subprocess.Popen(['./json_capture.sh'], stdout=subprocess.PIPE)
parseKey = ['detected_protocol_name',
            'host_server_name',
            'dns_host_name',
            'local_ip',
            'other_ip',
            'local_port',
            'other_port',
            'first_seen_at',
            'first_update_at',
            'last_seen_at']
while True:
    line = proc.stdout.readline().decode('utf-8').strip()
    if not line: break
    try:
        line = dict(json.loads(line))

        #Get only values of wg0 json
        if 'interface' not in line.keys() and line['interface'] != 'wg0':
            continue

        lineflow = line['flow']        
        #Generate data in dictionary form
        resultDict = {}
        for key in parseKey:
            try:
                if key.split('_')[-1]=="at":
                    resultDict[key] = getTimeKSTFromTimeStamp(int(lineflow[key])/1000)
                else:
                    resultDict[key] = lineflow[key]
            except Exception as e:
                resultDict[key] = 'NULL'

        #Save data with CSV
        if resultDict['local_ip'] != 'NULL':
            print(resultDict)
            filename=f"./csv/{resultDict['local_ip']}.csv"
            with open(filename, 'a', newline='') as f_object:
                dictwriter_object = DictWriter(f_object, fieldnames=parseKey)
                if os.path.getsize(filename) == 0:
                    dictwriter_object.writeheader()
                dictwriter_object.writerow(resultDict)
                f_object.close()

    except Exception as e:
        print(e)
