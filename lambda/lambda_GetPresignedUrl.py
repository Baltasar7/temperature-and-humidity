import json
import boto3
from datetime import datetime
from zoneinfo import ZoneInfo

s3 = boto3.client('s3')
BUCKET_NAME = ""


def lambda_handler(event, context):
    japan_time = datetime.now(ZoneInfo("Asia/Tokyo"))
    filename = f"sensor_data/{japan_time.year}/{japan_time.month}/{japan_time.day}/{japan_time.isoformat()}.json"

    url = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={'Bucket': BUCKET_NAME, 'Key': filename, 'ContentType': 'application/json'},
        ExpiresIn=60
    )

    return {
        'statusCode': 200,
        'body': json.dumps({'signed_url': url})
    }
