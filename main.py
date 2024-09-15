from flask import Flask, Response
import time
import json

app = Flask(__name__)

@app.route('/stream', methods=['POST'])
def stream():
    def generate():
        for i in range(10):
            ch = " A B C " * (i*5)
            payload = {"is_intent": False, "content": ch}
            yield f"{json.dumps(payload)}"
            time.sleep(0.3) 

    return Response(generate(), mimetype='application/json')

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=7998,debug=True)