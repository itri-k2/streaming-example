import random
from flask import Flask, Response
import time
import json

app = Flask(__name__)


@app.route('/stream', methods=['POST'])
def stream():
    def generate():
        # 讓api隨機有is_intent為true及false的兩種情境
        random_bit = random.randint(0, 1) 
        is_intent = random_bit == 0
        
        
        if is_intent:
            # 如果is_intent為true，回傳intent內容
            intent_payload_content = """{
        "polygon": "(138.5607, 15.7915), (99.8672, 89.0884), (72.0231, 16.6307), (138.5607, 76.9646)",
        "RAT": "NR",
        "DL ARFCN": "470503",
        "Weak RSRP ratio": "69",
        "Weak RSRP threshold": "-17",
        "Low SINR ratio": "72",
        "Low SINR threshold": "-91",
        "highDlPrbLoadRatioTarget": null,
        "MbpsaveDLRANUEThptTarget": null,
        "highDlPrbLoadRatioTarget.HighDlPrbLoad": null
    }"""
            intent_payload = json.loads(intent_payload_content)
            payload = {"is_intent": is_intent,
                           "details": intent_payload}
            yield f"{json.dumps(payload)}"

        else:
            # 如果is_intent為false，下方回傳一般對話
            for i in range(10):
                ch = " A B C " * (i*5)
                payload = {"is_intent": is_intent, "details": ch}
                yield f"{json.dumps(payload)}"
                time.sleep(0.3)

    return Response(generate(), mimetype='application/json')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=7998, debug=True)
