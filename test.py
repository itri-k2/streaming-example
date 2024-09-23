import requests
import json

url = "http://127.0.0.1:5000/is_intent"

headers = {
    "Content-Type": "application/json"
}

data = {
    "input_text": "Ensure that the radio network inside the area polygon (138.5607, 15.7915), (99.8672, 89.0884), (72.0231, 16.6307), (138.5607, 76.9646) with DL ARFCN is 470503 and RAT is NR meets Weak RSRP ratio is less than 69, where weak RSRP threshold is less than -17 Low SINR ratio is less than 72, where low SINR threshold is less than -91"
}


with requests.post(url, headers=headers, data=json.dumps(data), stream=True) as response:
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
