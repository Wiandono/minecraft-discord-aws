import base64
import json
import os
import time

import boto3
import requests
from discord_interactions import verify_key, InteractionType, InteractionResponseType

DISCORD_BASE_URL = 'https://discord.com/api/v10'

parameters = [
    {
        'ParameterKey': 'RecordName',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'Timezone',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'LevelType',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'PlayerIdleTimeout',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'ModrinthProjects',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'Difficulty',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'Memory',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'Snooper',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'EntryPoint',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'ViewDistance',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'DockerImageTag',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'MaxTickTime',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'SpotPrice',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'MaxPlayers',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'OnlineMode',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'ContainerInsights',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'YourIPv4',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'MinecraftTypeTag',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'SimulationDistance',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'UseAikarFlags',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'YourIPv6',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'SpawnProtection',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'LogGroupName',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'InstanceType',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'ECSAMI',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'AdminPlayerNames',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'KeyPairName',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'HostedZoneId',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'LogStreamPrefix',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'GameMode',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'Command',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'Seed',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'EnableRollingLogs',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'Whitelist',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'AutoPause',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'LogGroupRetentionInDays',
        'UsePreviousValue': True,
    },
    {
        'ParameterKey': 'MinecraftVersion',
        'UsePreviousValue': True,
    },
]


def verify_signature(event, decoded_body: bytes, dict_body: dict):
    signature = event['headers']['x-signature-ed25519']
    timestamp = event['headers']['x-signature-timestamp']

    if verify_key(decoded_body, signature, timestamp, os.getenv('BOT_PUBLIC_KEY')):
        return {
            'statusCode': 401,
            'body': json.dumps('Signature is invalid')
        }

    if dict_body['type'] == InteractionType.PING:
        return {
            'statusCode': 200,
            'body': json.dumps({'type': InteractionResponseType.PONG}),
        }


def send_reply(dict_body: dict, content):
    requests.post(
        '{0}/interactions/{1}/{2}/callback'.format(DISCORD_BASE_URL, dict_body['id'], dict_body['token']),
        json={
            'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            'data': {
                'tts': False,
                'content': content,
                'embeds': [],
            },
        },
    )


def update_reply(dict_body: dict, content):
    requests.patch(
        '{0}/webhooks/{1}/{2}/messages/@original'.format(
            DISCORD_BASE_URL, os.getenv('APPLICATION_ID'), dict_body['token']
        ),
        json={
            'content': content,
        }
    )


def monitor_start_server(dict_body: dict):
    update_reply(dict_body, 'Starting the server')
    is_update_not_finished = True

    while is_update_not_finished:
        time.sleep(10)

        stack_events = boto3.client('cloudformation').describe_stack_events(StackName=os.getenv('CF_STACK_NAME'))
        stack_event = stack_events['StackEvents'][0]

        if stack_event['LogicalResourceId'] == os.getenv('CF_STACK_NAME'):
            if stack_event['ResourceStatus'] == 'UPDATE_COMPLETE':
                update_reply(dict_body, 'Server started, getting IP address')
                get_server_ip_address(dict_body)
                is_update_not_finished = False
            elif stack_event['ResourceStatus'] == 'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS':
                update_reply(dict_body, 'Server cleanup in progress, almost there!')
        else:
            update_reply(dict_body, 'Server starting: Updating {0}'.format(stack_event['LogicalResourceId']))


def monitor_stop_server(dict_body: dict):
    update_reply(dict_body, 'Stopping the server')
    is_update_not_finished = True

    while is_update_not_finished:
        time.sleep(10)

        stack_events = boto3.client('cloudformation').describe_stack_events(StackName=os.getenv('CF_STACK_NAME'))
        stack_event = stack_events['StackEvents'][0]

        if stack_event['LogicalResourceId'] == os.getenv('CF_STACK_NAME'):
            if stack_event['ResourceStatus'] == 'UPDATE_COMPLETE':
                update_reply(dict_body, 'Server stopped')
                is_update_not_finished = False
            elif stack_event['ResourceStatus'] == 'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS':
                update_reply(dict_body, 'Server cleanup in progress, almost there!')
        else:
            update_reply(dict_body, 'Server stopping: Turning off {0}'.format(stack_event['LogicalResourceId']), )


def start_server(dict_body: dict):
    stacks = boto3.client('cloudformation').describe_stacks(StackName=os.getenv('CF_STACK_NAME'))
    stack = stacks['Stacks'][0]

    if stack['StackStatus'] == 'UPDATE_IN_PROGRESS':
        update_reply(dict_body, 'The server update is still in progress. Please wait a moment')

    for parameter in stack['Parameters']:
        if parameter['ParameterKey'] == 'ServerState' and parameter['ParameterValue'] == 'Running':
            update_reply(dict_body, 'The server is already running')

    parameters.append({
        'ParameterKey': 'ServerState',
        'ParameterValue': 'Running',
    })

    response = boto3.client('cloudformation').update_stack(
        StackName=os.getenv('CF_STACK_NAME'),
        UsePreviousTemplate=True,
        Parameters=parameters,
        Capabilities=['CAPABILITY_IAM'],
    )

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        monitor_start_server(dict_body)
    else:
        update_reply(dict_body, 'Cannot start the server, something bad happen :(')


def stop_server(dict_body: dict):
    stacks = boto3.client('cloudformation').describe_stacks(StackName=os.getenv('CF_STACK_NAME'))
    stack = stacks['Stacks'][0]

    if stack['StackStatus'] == 'UPDATE_IN_PROGRESS':
        update_reply(dict_body, 'The server update is still in progress. Please wait a moment')

    for parameter in stack['Parameters']:
        if parameter['ParameterKey'] == 'ServerState' and parameter['ParameterValue'] == 'Stopped':
            update_reply(dict_body, 'The server is already stopped')

    parameters.append({
        'ParameterKey': 'ServerState',
        'ParameterValue': 'Stopped',
    })

    response = boto3.client('cloudformation').update_stack(
        StackName=os.getenv('CF_STACK_NAME'),
        UsePreviousTemplate=True,
        Parameters=parameters,
        Capabilities=['CAPABILITY_IAM'],
    )

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        monitor_stop_server(dict_body)
    else:
        update_reply(dict_body, 'Cannot stop the server, something bad happen :(')


def get_server_ip_address(dict_body: dict):
    instances = boto3.client('ec2').describe_instances(
        Filters=[
            {
                'Name': 'tag:aws:cloudformation:stack-name',
                'Values': [os.getenv('CF_STACK_NAME')],
            },
            {
                'Name': 'instance-state-name',
                'Values': ['running'],
            },
        ],
    )

    if not instances['Reservations']:
        update_reply(dict_body, 'There is no server available. Start the server to start playing')

    instance = instances['Reservations'][0]['Instances'][0]

    if instance['State']['Name'] == 'pending':
        update_reply(dict_body, 'The server is still provisioning. Please wait a moment')
    elif instance['State']['Name'] in ('shutting-down', 'stopping', 'stopped'):
        update_reply(
            dict_body, 'The server is being turned off. Start the server again once the stop process is finished',
        )
    elif instance['State']['Name'] == 'terminated':
        update_reply(dict_body, 'The server is terminated. Start the server to start playing')

    update_reply(dict_body, 'IP Address: {0}'.format(instance['PublicIpAddress']))


def function(event, context):
    if 'python-requests' in event['headers']['User-Agent']:
        return {
            'statusCode': 200,
            'body': json.dumps('Health check from zappa deployment')
        }

    decoded_body = base64.b64decode(event['body'])
    dict_body = json.loads(decoded_body)

    verify_signature(event, decoded_body, dict_body)

    send_reply(dict_body, 'Thinking,...')

    if dict_body['data']['name'] == 'start':
        start_server(dict_body)
    elif dict_body['data']['name'] == 'stop':
        stop_server(dict_body)
    elif dict_body['data']['name'] == 'ip':
        get_server_ip_address(dict_body)
