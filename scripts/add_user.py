#!/usr/bin/env python3
from argparse import ArgumentParser

import boto3


def add_user(phone_number):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Users')
    table.put_item(
        Item={
            'phone': phone_number
        }
    )


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-p', '--phone')
    args = parser.parse_args()
    add_user(args.phone)
