# import os
# from csv  import DictWriter
# parseKey = ['detected_protocol_name',
#             'host_server_name',
#             'dns_host_name',
#             'local_ip',
#             'other_ip',
#             'local_port',
#             'other_port',
#             'first_seen_at',
#             'first_update_at',
#             'last_seen_at'
#             ]
#
# resultDict = {'detected_protocol_name': 'DNS', 'host_server_name': 'e10499.dsce9.akamaiedge.net', 'dns_host_name': 'NULL', 'local_ip': '10.0.0.3', 'other_ip': '1.1.1.1', 'local_port': 52390, 'other_port': 53, 'first_seen_at': 1662481488347, 'first_update_at': 1662481488347, 'last_seen_at': 1662481488350}
#
#
# while True:
#     with open(f"./{resultDict['local_ip']}.csv", 'a', newline='') as f_object:
#         dictwriter_object = DictWriter(f_object, fieldnames=parseKey)
#         if os.path.getsize(f"./{resultDict['local_ip']}.csv") == 0:
#             dictwriter_object.writeheader()
#         dictwriter_object.writerow(resultDict)
#         f_object.close()
#


times = 1662481497461

def getTimeKSTFromTimeStamp(timestamp):
    from datetime import timezone
    utctime = datetime.datetime.now(timezone.utc).strftime("%Y%m%d_%H:%M:%S")
    ostime = datetime.datetime.now().strftime("%Y%m%d_%H:%M:%S")

    if utctime == ostime:
        return (datetime.datetime.fromtimestamp(timestamp) + datetime.timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    else:
        return (datetime.datetime.fromtimestamp(timestamp)).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

import datetime

print(getTimeKSTFromTimeStamp(times/1000))
