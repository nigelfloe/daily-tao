import boto3

dynamodb = boto3.resource('dynamodb')

table = dynamodb.create_table(
    TableName='Users',
    KeySchema=[
        {
            'AttributeName': 'phone',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'phone',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)
