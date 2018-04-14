#!/usr/bin/env python3
import datetime
import json
import os
from io import BytesIO

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from bottle import Bottle, request, response, run

from wordwheel import (DEFAULT_OUTPUT_SIZE, get_word, make_image,
                       word_to_letters)

BUCKET_NAME = os.environ['WORDWHEEL_BUCKET_NAME']

app = Bottle()


@app.route('/')
def index():
    return ("<html><body><h1>Wordwheel</h1></body></html>")


@app.route('/generate/')
def generate():

    # Get some letters
    verbatim = bool(request.query.get('verbatim'))
    word = str(request.query.get('word', get_word()))
    letters = word_to_letters(word, verbatim)

    size = int(request.query.get('size', DEFAULT_OUTPUT_SIZE))

    filename = f"{''.join(letters)}_{size}.png"
    obj_key = os.path.join('images', filename)

    response_data = {}
    s3 = (boto3.session
          .Session(region_name='eu-west-2')
          .client('s3', config=Config(signature_version='s3v4'))
          )

    try:
        s3.get_object(Bucket=BUCKET_NAME, Key=obj_key)
    except ClientError as ex:
        # The image was not already found in S3. Generate it.
        if ex.response['Error']['Code'] == 'NoSuchKey':
            im = make_image(letters=letters, output_size=size)

            with BytesIO() as stream:
                im.save(stream, format='PNG')
                stream.seek(0)
                s3.upload_fileobj(stream, BUCKET_NAME, obj_key)
        else:
            raise ex

    obj_url = get_signed_obj_url(s3, obj_key)

    response_data = {
        "attachments": [
            {
                "fallback": "Wordwheel anagram puzzle image",
                "title": datetime.date.today().isoformat(),
                "image_url": obj_url,
                "footer": "Wordwheel",
                "ts": int(datetime.datetime.utcnow().timestamp()),
            }
        ]
    }

    response.content_type = 'application/json'
    return json.dumps(response_data)


def get_signed_obj_url(s3, obj_key):
    return s3.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': BUCKET_NAME,
            'Key': obj_key,
        },
        ExpiresIn=3600)


# run(app, host='localhost', port=8080, )
run(app, host='0.0.0.0')
