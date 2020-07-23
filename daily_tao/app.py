import json
from datetime import date

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
        twilio_creds = json.loads(
            secret_client.get_secret_value(SecretId='twilio')['SecretString'])
        twilio = Client(twilio_creds['account_sid'],
                        twilio_creds['auth_token'])
    for user in users:
        phone_number = user['phone']
        today = date.today().isoformat()
        last_chapter = (int(user['last_chapter']) if 'last_chapter' in user
                        else 0)
        last_sent_date = (user['last_sent_date'] if 'last_sent_date' in user
                          else None)
        if today == last_sent_date:
            print('{} already received chapter {} on {}'
                  .format(phone_number, last_chapter, last_sent_date))
        else:
            todays_chapter = str(last_chapter + 1)
            with open('tao.json') as tao_source:
                tao = json.load(tao_source)
            if todays_chapter in tao:
                print('sending chapter {} to {}'.format(todays_chapter,
                                                        phone_number))
                twilio.messages.create(
                    body=tao[todays_chapter],
                    from_='+12055798634',
                    to=phone_number)
                user['last_chapter'] = todays_chapter
            else:
                user['finished'] = True
            users_table.update_item(
                Key={'phone': user['phone']},
                UpdateExpression='SET last_chapter=:lc, finished=:f, '
                                 'last_sent_date=:lsd',
                ExpressionAttributeValues={
                    ':lc': todays_chapter,
                    ':f': user.get('finished', False),
                    ':lsd': today
                })
