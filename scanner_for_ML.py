import time, csv, math
from beacontools import BeaconScanner, IBeaconFilter

rssi_list = list()

d = '30'
f = d + '.csv'
counter = 0
sum_rssi = 0

#creat a csv
with open(f, "w") as csvfile:
    data_title = ['Distance', 'RSSI']
    writer = csv.DictWriter(csvfile, fieldnames = data_title)
    writer.writeheader()

# append a new row to csv
def append_csv(avg_rssi):
    with open(f, "a") as csvfile:
        data_title = ['Distance', 'RSSI']
        writer = csv.DictWriter(csvfile, fieldnames = data_title)
        data = {'Distance' : d, 'RSSI': avg_rssi}
        writer.writerow(data)

#calculate average rssi
def callback(bt_addr, rssi, packet, additional_info):
    #print("%s, %d" % (bt_addr, rssi))
    global rssi_list,sum_rssi,counter
    rssi_list.append(rssi)
    if len(rssi_list) >=10:
        rssi_list = rssi_list[-10:]
        avg_rssi = sum(sorted(rssi_list[1:8]))/8
        sum_rssi += avg_rssi
        counter += 1
        print("RSSI: "+ str(avg_rssi))
        append_csv(avg_rssi)

# scan for all iBeacon advertisements from beacons with the specified uuid
scanner = BeaconScanner(callback,
    device_filter=IBeaconFilter(uuid="426c7565-4368-6172-6d42-6561636f6e73")
)
scanner.start()
time.sleep(30)
print(sum_rssi/counter)
scanner.stop()