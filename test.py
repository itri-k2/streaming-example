import requests
import json



def send_request():
    # API endpoint
    url = 'http://localhost:8000/convert_to_3gpp_format'
    
    # Request headers
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Request body
    payload = {
        "polygon": "(138.5607, 15.7915), (99.8672, 89.0884), (72.0231, 16.6307), (138.5607, 76.9646)",
        "RAT": "NR",
        "DL ARFCN": "470503",
        "Weak RSRP ratio": "69",
        "Weak RSRP threshold": "-17",
        "Low SINR ratio": "72",
        "Low SINR threshold": "-91",
        "highDlPrbLoadRatioTarget": None,
        "MbpsaveDLRANUEThptTarget": None,
        "highDlPrbLoadRatioTarget.HighDlPrbLoad": None
    }
    
    try:
        # Send POST request
        response = requests.post(url, headers=headers, json=payload)
        
        # Check if request was successful
        response.raise_for_status()
 
        print(response.json()['response'])
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print('Error occurred:', e)
        return None

send_request()

# url = "http://127.0.0.1:8000/is_intent"

# headers = {
#     "Content-Type": "application/json"
# }

# # data = {
# #     "input_text": "Ensure that the radio network inside the area polygon (138.5607, 15.7915), (99.8672, 89.0884), (72.0231, 16.6307), (138.5607, 76.9646) with DL ARFCN is 470503 and RAT is NR meets Weak RSRP ratio is less than 69, where weak RSRP threshold is less than -17 Low SINR ratio is less than 72, where low SINR threshold is less than -91"
# # }

# data = {
#     "input_text": "how are you"}
# with requests.post(url, headers=headers, data=json.dumps(data), stream=True) as response:
#     if response.status_code == 200:
#         for chunk in response.iter_content(chunk_size=1024):
#             if chunk:
#                 try:
#                     decoded_chunk = chunk.decode('utf-8')
#                     json_data = json.loads(decoded_chunk)
#                     print(json_data)
#                 except json.JSONDecodeError:
#                     print(decoded_chunk)
#     else:
#         print(f"Error: {response.status_code}")
#         print(response.text)





import requests
import json


class StreamJSONDecoder:
    def __init__(self, url, headers, data, chunk_size=1024):
        self.url = url
        self.headers = headers
        self.data = data
        self.chunk_size = chunk_size

    def stream(self):
        with requests.post(self.url, headers=self.headers, json=self.data, stream=True) as response:
            if response.status_code == 200:
                for chunk in response.iter_content(chunk_size=self.chunk_size):
                    if chunk:
                        yield from self._process_chunk(chunk)
            else:
                yield {"error": f"HTTP Error: {response.status_code}", "details": response.text}

    def _process_chunk(self, chunk):
        try:
            decoded_chunk = chunk.decode('utf-8')
            json_data = json.loads(decoded_chunk)
            yield json_data
        except json.JSONDecodeError:
            yield {"raw": decoded_chunk}


def call_llm(message):

    # url = "http://127.0.0.1:8000/is_intent"
    # url = "http://127.0.0.1:7998/stream"
    url = "http://itri.yen-web.com/is_intent"

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "input_text": message,
    }
    decoder = StreamJSONDecoder(url, headers, data)
    return decoder

resp = call_llm("hello")
for item in resp.stream():
            print("test::::::" ,json.dumps(item))
            # if item["is_intent"]:

            #     payload = {"role":"assistant" ,"is_intent":item["is_intent"] , "content":item["details"]}

            # else:
            #     payload = {"role":"assistant" ,"is_intent":item["is_intent"] , "content":item["details"]}
            #     yield f"{json.dumps(payload)}"