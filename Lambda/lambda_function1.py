from decimal import Decimal
import json, boto3
import localization as lx
from botocore.exceptions import ClientError

# initialize the project with 2D LSE solver
P=lx.Project(mode = '2D', solver = 'LSE')

# add anchor points
P.add_anchor('anchore_A',(0,200))
P.add_anchor('anchore_B',(-200,200))
P.add_anchor('anchore_C',(0,0))

# add target
t,label=P.add_target()

def lambda_handler(event, context):

	from decimal import Decimal

	# get dis_A, dist_B, dist_C from DynamoDB
	dynamodb = boto3.resource('dynamodb')
	catFeed = dynamodb.Table('catFeed')

	db_key = 0

	try:
		response = catFeed.get_item(
			Key={
				'time': db_key
			}
		)
	except ClientError as e:
		print(e.response['Error']['Message'])
	else:
		item = response['Item']
		dist_A = float(item['dist_A'])
		dist_B = float(item['dist_B'])
		dist_C = float(item['dist_C'])

	time = event['time']

	if event['ID'] == "PI-1":
		dist_A = float(event['distance'])
	elif event['ID'] == "PI-2":
		dist_B = float(event['distance'])
	elif event['ID'] == "PI-3":
		dist_C = float(event['distance'])
        response = catFeed.put_item(Item = {'time': db_key, 'dist_A': Decimal(str(dist_A)), 'dist_B': Decimal(str(dist_B)), 'dist_C': Decimal(str(dist_C))})

    # solve the target location
	t.add_measure('anchore_A',dist_A*100)
	t.add_measure('anchore_B',dist_B*100)
	t.add_measure('anchore_C',dist_C*100)

	P.solve()

	# put target location into DynamoDB
	catPosition = dynamodb.Table('catPosition')
	response = catPosition.put_item(Item = {'time': time,'x': Decimal(str(t.loc.x)), 'y': Decimal(str(t.loc.y)), 'message':event['message']})
	return {
	'statusCode': 200,
	'body': json.dumps('Hello from Lamdba!')
	}
