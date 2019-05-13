#for MQTT (AWS IoT)
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

#for BLE
from beacontools import BeaconScanner, IBeaconFilter

import random, time, json, math, pigpio, serial
from time import gmtime, strftime
from datetime import datetime
from decimal import Decimal
from threading import Thread

import boto, boto3
import boto.dynamodb2
from boto.dynamodb2.table import Table
from boto.dynamodb2.fields import HashKey, RangeKey

#----------------------------------------------------------------------
# call AWS dynamodb

ACCOUNT_ID = ""
IDENTITY_POOL_ID = ""
ROLE_ARN = ""

cognito     = boto3.client('cognito-identity','us-east-1')
cognito_id  = cognito.get_id(AccountId=ACCOUNT_ID, IdentityPoolId=IDENTITY_POOL_ID)
oidc        = cognito.get_open_id_token(IdentityId=cognito_id['IdentityId'])

sts = boto3.client('sts')
assumedRoleObject = sts.assume_role_with_web_identity(
    RoleArn=ROLE_ARN,
    RoleSessionName="XX",
    WebIdentityToken=oidc['Token'])

client_dynamo = boto.dynamodb2.connect_to_region(
    'us-east-1',
    aws_access_key_id       = assumedRoleObject['Credentials']['AccessKeyId'],
    aws_secret_access_key   = assumedRoleObject['Credentials']['SecretAccessKey'],
    security_token          = assumedRoleObject['Credentials']['SessionToken'])


class dynamoDB:
    def __init__(self, db_name, partition_key_name):
        self.table_dynamo = None
        self.partition_key_name = partition_key_name
        try:
            self.table_dynamo = Table.create(db_name, schema=[HashKey(partition_key_name)], connection=client_dynamo)
            print ("Wait 20 sec until the table is created")
            time.sleep(20)
            print ("New table created.")
        except Exception as e:
            self.table_dynamo = Table(db_name, connection=client_dynamo)
            print ("Table already exists.")

    def add(self, **kwargs):
        try:
            record = self.get(kwargs[self.partition_key_name])
            for k,v in kwargs.items():
                record[k] = v
            record.save(overwrite=True)
            #print("Record has been updated.\n")
        except Exception as e:
            self.table_dynamo.put_item(data=kwargs)
            #print("New entry created.\n")

    def delete(self, pk):
        try:
            record = self.table_dynamo.get_item(**{self.partition_key_name:pk})
            self.table_dynamo.delete_item(**{self.partition_key_name:pk})
            #print("The record has been deleted.")
            return record
        except Exception as e:
            #print("Cannot delete the record, it does not exist.")
            pass
        return None

    def get(self,pk):
        try:
            item = self.table_dynamo.get_item(**{self.partition_key_name:pk})
            return item
        except Exception as e:
            #print("Cannot get the record, it does not exist.")
            pass
        return None

    def scan(self,**filter_kwargs):
        return self.table_dynamo.scan(**filter_kwargs)

#----------------------------------------------------------------------

#----------------------------------------------------------------------
# get and send weight

def get_weight():
    s = serial.Serial('/dev/ttyUSB0', 9600, timeout = 5)
    weight = ""

    #read from Arduino
    while 1:
        char = s.read().decode("utf-8")
        if char != "\n":
            weight += char
        else:
            if float(weight) >= 0.3:
                db = dynamoDB("catFeed","time")
                db.add(**{
                    "time": int(time.mktime(datetime.now().timetuple()))//86400,
                    "weight": Decimal(weight)
                })
                print(float(weight))
            weight = ""
        time.sleep(0.2)

#----------------------------------------------------------------------

#----------------------------------------------------------------------
#servo control
        
def toggle_servo():
    # connect to the 
    pi = pigpio.pi()

    # loop forever
    while True:
        #connect to DB
        db = dynamoDB("catFeed","time")
        item = db.get(int(time.mktime(datetime.now().timetuple()))//86400)
        motion = item['motion']
        print(motion)
        
        pi.set_servo_pulsewidth(12, 500) # position anti-clockwise
        time.sleep(motion/10000)
        pi.set_servo_pulsewidth(12, 1450) # middle
        time.sleep(10)

#----------------------------------------------------------------------

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
clientId = "PI-1"
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
        message['ID'] = "PI-1"
        message['time'] = int(time.mktime(datetime.now().timetuple()))
        message['distance'] = str(calculateAccuracy(-64.0,avg_rssi))
        message['message'] = "hello"
        messageJson = json.dumps(message)
        
        myAWSIoTMQTTClient.publish(topic, messageJson, 1)
        print('Published topic %s: %s\n' % (topic, messageJson))

#start mqtt_iBeacon
def mqtt_iBeacon():
    scanner = BeaconScanner(callback, device_filter=IBeaconFilter(uuid="426c7565-4368-6172-6d42-6561636f6e73"))
    scanner.start()
        
#----------------------------------------------------------------------

#----------------------------------------------------------------------
# main: start 3 thread

try:
    thread_mqtt = Thread(name='mqtt_iBeacon', target = mqtt_iBeacon)
    thread_mqtt.start()
    
    thread_weight = Thread(name='get_weight', target = get_weight)
    thread_weight.start()
    
    thread_servo = Thread(name='toggle_servo', target = toggle_servo)
    thread_servo.start()
    
except KeyboardInterrupt:
    thread_mqtt.stop()
    thread_weight.stop()
    thread_servo.stop()
