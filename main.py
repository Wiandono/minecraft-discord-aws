import base64
import json
import os

import boto3
from discord_interactions import verify_key, InteractionType, InteractionResponseType

cloudformation = boto3.client('cloudformation')
ec2 = boto3.client('ec2')

parameters = [
    {
        "ParameterKey": "RecordName",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "Timezone",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "LevelType",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "PlayerIdleTimeout",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "ModrinthProjects",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "Difficulty",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "Memory",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "Snooper",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "EntryPoint",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "ViewDistance",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "DockerImageTag",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "MaxTickTime",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "SpotPrice",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "MaxPlayers",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "OnlineMode",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "ContainerInsights",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "YourIPv4",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "MinecraftTypeTag",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "SimulationDistance",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "UseAikarFlags",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "YourIPv6",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "SpawnProtection",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "LogGroupName",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "InstanceType",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "ECSAMI",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "AdminPlayerNames",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "KeyPairName",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "HostedZoneId",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "LogStreamPrefix",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "GameMode",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "Command",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "Seed",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "EnableRollingLogs",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "Whitelist",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "AutoPause",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "LogGroupRetentionInDays",
        "UsePreviousValue": True,
    },
    {
        "ParameterKey": "MinecraftVersion",
        "UsePreviousValue": True,
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


def start_server() -> str:
    stacks = cloudformation.describe_stacks(StackName=os.getenv('CF_STACK_NAME'))
    stack = stacks['Stacks'][0]

    if stack['StackStatus'] == 'UPDATE_IN_PROGRESS':
        return 'The server update is still in progress. Please wait a moment'

    for parameter in stack['Parameters']:
        if parameter['ParameterKey'] == 'ServerState' and parameter['ParameterValue'] == 'Running':
            return 'The server is already running'

    parameters.append({
        'ParameterKey': 'ServerState',
        'ParameterValue': 'Running',
    })

    response = cloudformation.update_stack(
        StackName=os.getenv('CF_STACK_NAME'),
        UsePreviousTemplate=True,
        Parameters=parameters,
        Capabilities=['CAPABILITY_IAM'],
    )

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return 'Starting the server'

    return 'Cannot start the server, something bad happen :('


def stop_server():
    stacks = cloudformation.describe_stacks(StackName=os.getenv('CF_STACK_NAME'))
    stack = stacks['Stacks'][0]

    if stack['StackStatus'] == 'UPDATE_IN_PROGRESS':
        return 'The server update is still in progress. Please wait a moment'

    for parameter in stack['Parameters']:
        if parameter['ParameterKey'] == 'ServerState' and parameter['ParameterValue'] == 'Stopped':
            return 'The server is already stopped'

    parameters.append({
        'ParameterKey': 'ServerState',
        'ParameterValue': 'Stopped',
    })

    response = cloudformation.update_stack(
        StackName=os.getenv('CF_STACK_NAME'),
        UsePreviousTemplate=True,
        Parameters=parameters,
        Capabilities=['CAPABILITY_IAM'],
    )

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return 'Stopping the server'

    return 'Cannot stop the server, something bad happen :('


def get_server_ip_address():
    instances = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:aws:cloudformation:stack-name',
                'Values': [os.getenv('CF_STACK_NAME')],
            },
        ],
    )

    if not instances['Reservations']:
        return 'There is no server available. Start the server to start playing'

    instance = instances['Reservations']['Instances'][0]

    if instance['State']['Name'] == 'pending':
        return 'The server is still provisioning. Please wait a moment'
    elif instance['State']['Name'] in ('shutting-down', 'stopping', 'stopped'):
        return 'The server is being turned off. Start the server again once the stop process is finished'
    elif instance['State']['Name'] == 'terminated':
        return 'The server is terminated. Start the server to start playing'

    return instances['PublicIpAddress']


def function(event, context):
    if 'python-requests' in event['headers']['User-Agent']:
        return {
            'statusCode': 200,
            'body': json.dumps('Health check from zappa deployment')
        }

    decoded_body = base64.b64decode(event['body'])
    dict_body = json.loads(decoded_body)

    verify_signature(event, decoded_body, dict_body)

    response = 'Bangun zar'

    if dict_body['data']['name'] == 'start':
        response = start_server()
    elif dict_body['data']['name'] == 'stop':
        response = stop_server()
    elif dict_body['data']['name'] == 'ip':
        response = get_server_ip_address()

    return {
        'statusCode': 200,
        'body': json.dumps({
            'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            'data': {
                'tts': False,
                'content': response,
                'embeds': [],
                'allowed_mentions': [],
            },
        }),
    }
