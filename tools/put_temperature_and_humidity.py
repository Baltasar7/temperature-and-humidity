import time
import json
import requests

API_GATEWAY_URL = ""


def get_presigned_url():
    try:
        response = requests.get(API_GATEWAY_URL)
        data = response.json()
        return data.get('signed_url')
    except Exception as e:
        print(f"Failed to get presigned URL: {e}")
        return None


def send_data():
    temperature = 4.2
    humidity = 35
    if humidity is not None and temperature is not None:
        payload = {
            "temperature": round(temperature, 2),
            "humidity": round(humidity, 2),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        presigned_url = get_presigned_url()
        if presigned_url:
            headers = {'Content-Type': 'application/json'}
            response = requests.put(presigned_url, data=json.dumps(payload), headers=headers)
            if response.status_code == 200:
                print("Data successfully uploaded to S3")
            else:
                print(f"Failed to upload data: {response.status_code}")
        else:
            print("Could not obtain presigned URL.")
    else:
        print("Failed to read sensor data.")


if __name__ == "__main__":
    send_data()