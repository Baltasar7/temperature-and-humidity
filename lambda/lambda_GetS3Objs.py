import boto3
import json
from datetime import datetime, timedelta

s3 = boto3.client('s3')
BUCKET_NAME = ""

def lambda_handler(event, context):
    try:
        query_params = event.get("queryStringParameters", {})
        start_date = query_params.get("startDate")
        end_date = query_params.get("endDate")
        if not start_date or not end_date:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing startDate or endDate"})
            }
        try:
            start_dt = datetime.strptime(start_date, "%Y%m%d")
            end_dt = datetime.strptime(end_date, "%Y%m%d")
        except ValueError:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid date format. Use YYYYMMDD."})
            }

        data_list = []
        current_date = start_dt
        while current_date <= end_dt:
            year = current_date.strftime('%Y')
            month = str(current_date.month)
            day = str(current_date.day)
            prefix = f"sensor_data/{year}/{month}/{day}/"

            try:
                response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
                if "Contents" in response:
                    for obj in response["Contents"]:
                        file_key = obj["Key"]
                        file_response = s3.get_object(Bucket=BUCKET_NAME, Key=file_key)
                        file_content = file_response["Body"].read().decode("utf-8")
                        json_data = json.loads(file_content)
                        data_list.append(json_data)
            except Exception as e:
                print(f"Error fetching data from {prefix}: {str(e)}")

            current_date += timedelta(days=1)

        print(f"{data_list}")
        return {
            "statusCode": 200,
            "body": json.dumps(data_list)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
