#for MQTT (AWS IoT)
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

#for BLE
from beacontools import BeaconScanner, IBeaconFilter

import random, time, json, math
from time import gmtime, strftime
from datetime import datetime


#----------------------------------------------------------------------
# MQTT (AWS IoT)

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")

host = ""
rootCAPath = ""
certificatePath = ""
privateKeyPath = ""

port = 8883
useWebsocket = False
clientId = "PI-3"
topic = "IoT/Location"

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
myAWSIoTMQTTClient.configureEndpoint(host, port)
myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()

#----------------------------------------------------------------------


#----------------------------------------------------------------------
# BLE get RSSI

rssi_list = list()

def calculateAccuracy(txPower, rssi):
    if rssi == 0:
        return -1 # if we cannot determine accuracy, return -1.
    ratio = rssi * 1 / txPower;
    if ratio < 1.0:
        return math.pow(ratio, 10)
    else:
        return (1.34458138) * math.pow(ratio, 9.012648385) + 0.15541862

#calculate average rssi
def callback(bt_addr, rssi, packet, additional_info):
    global rssi_list
    global topic
    
    rssi_list.append(rssi)
    if len(rssi_list) >=10:
        rssi_list = rssi_list[-10:]
        avg_rssi = sum(sorted(rssi_list[1:8]))/8
        print("RSSI: "+ str(avg_rssi))
        print("Distance: "+ str(calculateAccuracy(-64.0,avg_rssi)))
        
        message = {}
        message['ID'] = "PI-2"
        message['time'] = int(time.mktime(datetime.now().timetuple()))
        message['distance'] = str(calculateAccuracy(-64.0,avg_rssi))
        message['message'] = "hello"
        messageJson = json.dumps(message)
        
        myAWSIoTMQTTClient.publish(topic, messageJson, 1)
        print('Published topic %s: %s\n' % (topic, messageJson))
        
#----------------------------------------------------------------------


while True:
    scanner = BeaconScanner(callback,
    device_filter=IBeaconFilter(uuid="426c7565-4368-6172-6d42-6561636f6e73"))
  
    scanner.start()
    time.sleep(30)
    scanner.stop()

