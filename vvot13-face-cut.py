import boto3
import os
import io
import json
import uuid
import ydb
from sanic import Sanic
from PIL import Image

app = Sanic(__name__)

aws_access_key_id = os.getenv('aws_access_key_id')
aws_secret_access_key = os.getenv('aws_secret_access_key')
photos_bucket = os.getenv('photos_bucket')
faces_bucket = os.getenv('faces_bucket')
ydb_endpoint = os.getenv('ydb_endpoint')
ydb_database = os.getenv('ydb_database')

driver = ydb.Driver(endpoint=ydb_endpoint, database=ydb_database)
driver.wait(fail_fast=True, timeout=5)
pool = ydb.SessionPool(driver)

session = boto3.session.Session()
s3 = session.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)


@app.after_server_start
async def after_server_start(app, loop):
    print(f"App listening at port {os.environ['port']}")


@app.post('/', methods=['POST'])
async def crop_image(request):
    body = json.loads(request.json['messages'][0]['details']['message']['body'])
    image_object = io.BytesIO()
    object_id = body['object_id']
    coordinates = body['coordinates']

    s3.download_fileobj(photos_bucket, object_id, image_object)
    image = Image.open(image_object)

    cropped_image = image.crop(
        (
            int(coordinates[0]['x']),
            int(coordinates[0]['y']),
            int(coordinates[2]['x']),
            int(coordinates[2]['y'])
        )
    )

    cropped_face_id = str(uuid.uuid4())
    cropped_image_file = io.BytesIO()
    cropped_image.save(cropped_image_file, format="JPEG")
    cropped_image_file.seek(0)
    s3.upload_fileobj(cropped_image_file, faces_bucket, f'{cropped_face_id}.jpg')

    db_session = driver.table_client.session().create()
    db_session.transaction().execute(
        f'INSERT INTO face_table (cropped_face_id, face_name, original_image_id) values (\"{cropped_face_id}\", null, \"{object_id}\");',
        commit_tx=True,
    )


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ['port']), motd=False, access_log=False)
