import requests
import json

url = "http://localhost:7998/stream"

headers = {
    "Content-Type": "application/json"
}



with requests.post(url, headers=headers,  stream=True) as response:
    if response.status_code == 200:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                try:
                    decoded_chunk = chunk.decode('utf-8')
                    json_data = json.loads(decoded_chunk)
                    print(json_data)
                except json.JSONDecodeError:
                    print(decoded_chunk)
    else:
        print(f"Error: {response.status_code}")
        print(response.text)