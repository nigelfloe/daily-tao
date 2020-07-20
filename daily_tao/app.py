import json

import boto3
from boto3.dynamodb.conditions import Attr
from twilio.rest import Client


def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    users_table = dynamodb.Table('Users')
    users = users_table.scan(
        FilterExpression=Attr('finished').ne(True))['Items']
    if users:
        aws_session = boto3.session.Session()
        secret_client = aws_session.client(service_name='secretsmanager')
        twilio_creds = (secret_client.get_secret_value(SecretId='twilio')
                        ['SecretString'])
        twilio = Client(twilio_creds['account_sid'],
                        twilio_creds['auth_token'])
    for user in users:
        last_chapter = (int(user['last_chapter']) if 'last_chapter' in user
                        else 0)
        todays_chapter = str(last_chapter + 1)
        with open('tao.json') as tao_source:
            tao = json.load(tao_source)
        if todays_chapter in tao:
            twilio.messages.create(
                body=tao[todays_chapter],
                from_='+12055798634',
                to=user['phone'])
            user['last_chapter'] = todays_chapter
        else:
            user['finished'] = True
        users_table.update_item(
            Key={'phone': user['phone']},
            UpdateExpression='SET last_chapter=:lc, finished=:f',
            ExpressionAttributeValues={
                ':lc': todays_chapter,
                ':f': user.get('finished', False)
            })
