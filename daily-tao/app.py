import json

import boto3
from boto3.dynamodb.conditions import Attr


def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    users_table = dynamodb.Table('Users')
    users = users_table.scan(
        FilterExpression=Attr('finished').ne(True))['Items']
    for user in users:
        last_chapter = (int(user['last_chapter']) if 'last_chapter' in user
                        else 0)
        todays_chapter = str(last_chapter + 1)
        with open('tao.json') as tao_source:
            tao = json.load(tao_source)
        if todays_chapter in tao:
            sns = boto3.client('sns')
            sns.publish(PhoneNumber=user['phone'], Message=tao[todays_chapter])
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
