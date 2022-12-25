import boto3
import os
import requests
import base64
import json

aws_access_key_id = os.getenv('aws_access_key_id')
aws_secret_access_key = os.getenv('aws_secret_access_key')
session = boto3.session.Session()
s3 = session.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)
sqs = session.client(
    service_name='sqs',
    endpoint_url='https://message-queue.api.cloud.yandex.net',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name='ru-central1'
)
queue_url = os.getenv('queue_url')
token = 'Bearer ' + os.getenv('token')
folder_id = os.getenv('folder_id')

def handler(event, context):
    bucket_id = event['messages'][0]['details']['bucket_id']
    object_id = event['messages'][0]['details']['object_id']
    image_file = s3.get_object(Bucket=bucket_id, Key=object_id)['Body'].read()
    encoded_file = base64.b64encode(image_file).decode('UTF-8')
    data = json.dumps({
        'folderId': folder_id,
        'analyze_specs': [{
            'content': encoded_file,
            'features': [{
                'type': 'FACE_DETECTION'
            }]
        }]
    })
    headers = { 'Authorization': token }
    response = requests.post('https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze', data=data, headers=headers)
    faces = response.json()['results'][0]['results'][0]['faceDetection']['faces']
    for face in faces:
        coordinates = (face['boundingBox']['vertices'])
        message = json.dumps({
            'object_id': object_id,
            'coordinates': coordinates
        })
        sqs.send_message(QueueUrl=queue_url, MessageBody=message)
