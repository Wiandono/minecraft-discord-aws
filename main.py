import base64
import json
import os

from discord_interactions import verify_key, InteractionType, InteractionResponseType


def verify_signature(event, decoded_body: bytes) -> bool:
    signature = event['headers']['x-signature-ed25519']
    timestamp = event['headers']['x-signature-timestamp']

    return verify_key(decoded_body, signature, timestamp, os.getenv('BOT_PUBLIC_KEY'))


def function(event, context):
    print(event)

    if 'python-requests' in event['headers']['User-Agent']:
        return {
            'statusCode': 200,
            'body': json.dumps('Health check from zappa deployment')
        }

    decoded_body = base64.b64decode(event['body'])

    if not verify_signature(event, decoded_body):
        return {
            'statusCode': 401,
            'body': json.dumps('Signature is invalid')
        }

    dict_body = json.loads(decoded_body)

    if dict_body['type'] == InteractionType.PING:
        return {
            'statusCode': 200,
            'body': json.dumps({'type': InteractionResponseType.PONG}),
        }

    return {
        'statusCode': 200,
        'body': json.dumps({
            'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            'data': {
                'tts': False,
                'content': 'Bangun zar',
                'embeds': [],
                'allowed_mentions': [],
            }
        }),
    }
