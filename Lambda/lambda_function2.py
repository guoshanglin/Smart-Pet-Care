import json
import boto3
import time
import math
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    timestamp = int(time.mktime(datetime.now().timetuple()))//86400
    dynamodb = boto3.resource('dynamodb')
    catFeed = dynamodb.Table("catFeed")
    
    # get record from DynamoDB
    try:
        response = catFeed.get_item(
            Key={
                'time': timestamp
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        try:
            item = response['Item']
            motion = int(item['motion'])
        except KeyError:
            response = catFeed.get_item(
                Key={
                    'time': timestamp-1
                }
            )
            item = response['Item']
            motion = 0

        # get last location from the latest record
        last_x = int(item['last_x'])
        last_y = int(item['last_y'])
    
        # get new location
        try:
            new_x = int(float(event['Records'][0]['dynamodb']['NewImage']['x']['N']))
            new_y = int(float(event['Records'][0]['dynamodb']['NewImage']['y']['N']))
        except:
            new_x = int(float(event['Records'][0]['dynamodb']['OldImage']['x']['N']))
            new_y = int(float(event['Records'][0]['dynamodb']['OldImage']['y']['N']))
            
        # calculate change in location
        motion_add = int(math.sqrt((new_x-last_x)*(new_x-last_x) + (new_y-last_y)*(new_y-last_y)))
        motion += motion_add
        if motion_add > 100:
            active = 1
        else:
            active = 0

        # update database with new motion, and active/not active
        response = catFeed.put_item(Item = {'time': timestamp, 'date': str(datetime.now().date()), 'last_x': new_x, 'last_y': new_y, 'motion': motion, 'eaten': item['eaten'], 'weight': item['weight'], 'active': active})
    
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

