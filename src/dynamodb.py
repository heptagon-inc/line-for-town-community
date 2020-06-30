import os

import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr, And, Or

dynamodb = boto3.resource("dynamodb")


def create_user_if_needed(user_id):
    users_table_name = os.environ['USERS_TABLE_NAME']

    try:
        users = dynamodb.Table(users_table_name).scan(
            FilterExpression=Attr('id').eq(user_id)
        )
        
        if users["Count"] == 0:
            item = {
              'id': user_id,
              'is_enabled': True,
              'gomi_today': '07:00',
              'gomi_day_before': '18:00'
            }
    
            response = dynamodb.Table(users_table_name).put_item(Item=item)
        else:
            pass
    except ClientError as e:
        print(e.response['Error']['Message'])
        
        
def get_user(user_id):
    users_table_name = os.environ['USERS_TABLE_NAME']

    try:
        users = dynamodb.Table(users_table_name).scan(
            FilterExpression=Attr('id').eq(user_id)
        )
        
        if users["Count"] == 1:
            return users["Items"][0]
        else:
            return None
    except ClientError as e:
        print(e.response['Error']['Message'])
        return None
    

def enable_user(user_id):
    users_table_name = os.environ['USERS_TABLE_NAME']

    try:
        response = dynamodb.Table(users_table_name).update_item(
            Key={
                'id': user_id
            },
            UpdateExpression="set #enabled = :b",
            ExpressionAttributeNames={
                '#enabled': 'is_enabled',
            },
            ExpressionAttributeValues={
                ':b': True
            },
            ReturnValues="UPDATED_NEW"
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    

def disable_user(user_id):
    users_table_name = os.environ['USERS_TABLE_NAME']

    try:
        response = dynamodb.Table(users_table_name).update_item(
            Key={
                'id': user_id
            },
            UpdateExpression="set #enabled = :b",
            ExpressionAttributeNames={
                '#enabled': 'is_enabled'
            },
            ExpressionAttributeValues={
                ':b': False
            },
            ReturnValues="UPDATED_NEW"
        )
    except ClientError as e:
        print(e.response['Error']['Message'])


def set_column_to_users_table(user_id, column_name, new_value):
    users_table_name = os.environ['USERS_TABLE_NAME']

    try:
        response = dynamodb.Table(users_table_name).update_item(
            Key={
                'id': user_id
            },
            UpdateExpression="set #col = :v",
            ExpressionAttributeNames={
                '#col': column_name
            },
            ExpressionAttributeValues={
                ':v': new_value
            },
            ReturnValues="UPDATED_NEW"
        )
        
        return True
    except ClientError as e:
        print(e.response['Error']['Message'])
        return False


def remove_column_from_users_table(user_id, column_name):
    users_table_name = os.environ['USERS_TABLE_NAME']

    try:
        response = dynamodb.Table(users_table_name).update_item(
            Key={
                'id': user_id
            },
            UpdateExpression="remove #col",
            ExpressionAttributeNames={
                '#col': column_name
            },
            ReturnValues="UPDATED_NEW"
        )
        
        return True
    except ClientError as e:
        print(e.response['Error']['Message'])
        return False


def insert_schedule_data(schedule_id, prefix, weekday, category):
    schedules_table_name = os.environ['SCHEDULES_TABLE_NAME']

    try:
        item = {
            'id': schedule_id,
            'prefix': prefix,
            'weekday': weekday,
            'category': category
        }

        response = dynamodb.Table(schedules_table_name).put_item(Item=item)
    except ClientError as e:
        print(e.response['Error']['Message'])


def scan_schedule_data(prefix, weekday_ja):
    schedules_table_name = os.environ['SCHEDULES_TABLE_NAME']

    try:
        filter_exp = And(
            Attr('weekday').eq(weekday_ja), 
            Or(
                Attr('prefix').eq(0), 
                Attr('prefix').eq(prefix)
            )
        )

        response = dynamodb.Table(schedules_table_name).scan(
            FilterExpression=filter_exp
        )
        
        return response['Items']
    except ClientError as e:
        print(e.response['Error']['Message'])
        return []
        
    
def scan_users_who_need_to_push(column_name, hour_min):
    users_table_name = os.environ['USERS_TABLE_NAME']

    try:
        filter_exp = Attr(column_name).eq(hour_min) & Attr('is_enabled').eq(True)

        response = dynamodb.Table(users_table_name).scan(
            FilterExpression=filter_exp
        )
        
        return response['Items']
    except ClientError as e:
        print(e.response['Error']['Message'])
        return []