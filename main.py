from flask import Flask, request, jsonify, Response
from transformers import pipeline
import torch
import re
import json
import time

app = Flask(__name__)

# class IntentHandler:
#     def __init__(self, model_pipeline):
#         self.model_pipeline = model_pipeline

#     def handle_intent(self, user_input):
#         response = self.model_pipeline([{"role": "user", "content": user_input}], max_new_tokens=512)
#         translated_text = response[0]['generated_text'][-1]['content']
#         print(f"Translated Intent: {translated_text}")
#         return translated_text

def initialize_pipeline(model_name):
    device = 0 if torch.cuda.is_available() else -1
    return pipeline("text-generation", model=model_name, device=device, torch_dtype="auto")

intent_pipe = initialize_pipeline("meta-llama/Meta-Llama-3-8B-Instruct")
conversation_pipe = initialize_pipeline("microsoft/Phi-3-mini-4k-instruct")  # 替換為處理日常對話的模型

# intent_handler = IntentHandler(intent_pipe)

def extract_keywords_from_response(input_text):
    messages = [
        {
            "role": "system",
            "content": "Classify input as intent if it contains: 'polygon', 'RAT', 'DL ARFCN', 'Weak RSRP ratio', 'Weak RSRP threshold', 'Low SINR ratio', 'Low SINR threshold', 'Average DL RAN UE Throughput', 'Low DL RAN UE Throughput Ratio', 'Low DL RAN UE Throughput Threshold', 'Average UL RAN UE Throughput', 'Low UL RAN UE Throughput Ratio', 'Low UL RAN UE Throughput Threshold', 'Average DL PRB Load', 'Average UL PRB Load', 'High DL PRB Load Ratio', 'High DL PRB Load Threshold', 'High UL PRB Load Ratio', 'High UL PRB Load Threshold'. Extract each keyword's value, and list it in dictionary. If no value is found, store None. Ensure 'polygon' and all other keywords have their values captured correctly in the dictionary. If none of these keywords are present, classify as normal conversation and have a normal conversation."
        },
        {"role": "user", "content": input_text},
    ]

    response = intent_pipe(messages, max_new_tokens=512)
    response_text = response[0]['generated_text'][-1]['content']
    print(response_text)

    keywords = {}
    # Improved pattern to handle different cases, especially for 'polygon'
    key_value_pattern = re.compile(r'^\s*[*-]?\s*([\w\s\.\'\-]+):\s*(.+)$')

    expected_keys = {
        'polygon', 'RAT', 'DL ARFCN', 'Weak RSRP ratio', 
        'Weak RSRP threshold', 'Low SINR ratio', 
        'Low SINR threshold', 'Average DL RAN UE Throughput', 
        'Low DL RAN UE Throughput Ratio', 'Low DL RAN UE Throughput Threshold', 
        'Average UL RAN UE Throughput', 'Low UL RAN UE Throughput Ratio', 
        'Low UL RAN UE Throughput Threshold', 'Average DL PRB Load', 
        'Average UL PRB Load', 'High DL PRB Load Ratio', 
        'High DL PRB Load Threshold', 'High UL PRB Load Ratio', 
        'High UL PRB Load Threshold'
    }

    # Fields that should keep their original string values without numeric extraction
    non_numeric_keys = {'RAT'}


    # Extract values from response
    for line in response_text.splitlines():
        match = key_value_pattern.match(line)
        if match:
            key = match.group(1).strip().strip("'\"")
            value = match.group(2).strip().strip("'\",}")

            # Remove any unwanted characters from the value
            value = re.sub(r"[\"'{}]+", "", value).strip()
            
            # Special handling for 'polygon' key to capture complex coordinate values properly
            if key == 'polygon':
                # Ensure to capture coordinate-like values properly, and clean the output
                value = re.sub(r"[^\d.,\s()-]", "", value)  # Remove non-coordinate characters
                value = re.sub(r'\s+', ' ', value).strip()  # Normalize spaces
                keywords[key] = value
            elif key in expected_keys:
                if value == "None":
                    value = ""
                else:
                    if key not in non_numeric_keys:
                        numeric_value = re.findall(r'-?\d+\.?\d*', value)
                        value = numeric_value[0] if numeric_value else ""
                keywords[key] = value
    
    # Ensure all expected keys are in the dictionary
    for key in expected_keys:
        if key not in keywords:
            keywords[key] = ""  # or None depending on your preference

    # Check if "ITRI" is mentioned in input_text and add to keywords if so
    if "itri" in input_text.lower():
        keywords["objectInstance"] = "ITRI"
    else:
        keywords["objectInstance"] = ""

    print(f"Extracted Keywords: {keywords}")
    return keywords



def determine_intent_type(keywords):
    # Filter out empty string values
    filtered_keywords = {k: v for k, v in keywords.items() if v != ""}

    if any(key in filtered_keywords for key in ["Weak RSRP ratio", "Low SINR ratio", "Weak RSRP threshold", "Low SINR threshold"]):
        return "Coverage Intent"
    elif any(key in filtered_keywords for key in ["Average DL RAN UE Throughput", "Low DL RAN UE Throughput Ratio", "Low DL RAN UE Throughput Threshold", "Average UL RAN UE Throughput", "Low UL RAN UE Throughput Ratio", "Low UL RAN UE Throughput Threshold"]):
        return "UE Throughput Intent"
    elif any(key in filtered_keywords for key in ["Average DL PRB Load", "Average UL PRB Load", "High DL PRB Load Ratio", "High DL PRB Load Threshold", "High UL PRB Load Ratio", "High UL PRB Load Threshold"]):
        return "RAN Capacity Intent"
    else:
        return "Unknown Intent"


@app.route("/is_intent/", methods=["POST"])
def is_intent():
    input_data = request.json
    input_text = input_data.get('input_text', '')

    def generate_response():
        extracted_keywords = extract_keywords_from_response(input_text)

        all_none = all(value == "" for value in extracted_keywords.values())

        output_data = {}

        if all_none:
            # 如果所有的關鍵字都是 None，則將 input_text 發送給處理普通對話的模型
            conversation_response = conversation_pipe([{"role": "user", "content": input_text}], max_new_tokens=512)
            conversation_text = conversation_response[0]['generated_text'][-1]['content']

            output_data = {
                "is_intent": "Conversation",
                "details": conversation_text.strip()
            }
        else:      
            # Determine the type of intent based on extracted keywords
            intent_type = determine_intent_type(extracted_keywords)

            if intent_type == "Coverage Intent":
                output_data = {
                    "is_intent": "Coverage",
                    "details": {
                        "objectInstance": extracted_keywords.get("objectInstance", ""),
                        "polygon": extracted_keywords.get("polygon", ""),
                        "RAT": extracted_keywords.get("RAT", ""),
                        "DL ARFCN": extracted_keywords.get("DL ARFCN", ""),
                        "Weak RSRP ratio": extracted_keywords.get("Weak RSRP ratio", ""),
                        "Weak RSRP threshold": extracted_keywords.get("Weak RSRP threshold", ""),
                        "Low SINR ratio": extracted_keywords.get("Low SINR ratio", ""),
                        "Low SINR threshold": extracted_keywords.get("Low SINR threshold", "")
                    }
                }
            elif intent_type == "UE Throughput Intent":
                output_data = {
                    "is_intent": "UEthroughput",
                    "details": {
                        "objectInstance": extracted_keywords.get("objectInstance", ""),
                        "polygon": extracted_keywords.get("polygon", ""),
                        "RAT": extracted_keywords.get("RAT", ""),
                        "DL ARFCN": extracted_keywords.get("DL ARFCN", ""),
                        "Average DL RAN UE Throughput": extracted_keywords.get("Average DL RAN UE Throughput", ""),
                        "Low DL RAN UE Throughput Ratio": extracted_keywords.get("Low DL RAN UE Throughput Ratio", ""),
                        "Low DL RAN UE Throughput Threshold": extracted_keywords.get("Low DL RAN UE Throughput Threshold", ""),
                        "Average UL RAN UE Throughput": extracted_keywords.get("Average UL RAN UE Throughput", ""),
                        "Low UL RAN UE Throughput Ratio": extracted_keywords.get("Low UL RAN UE Throughput Ratio", ""),
                        "Low UL RAN UE Throughput Threshold": extracted_keywords.get("Low UL RAN UE Throughput Threshold", "")
                    }
                }
            elif intent_type == "RAN Capacity Intent":
                output_data = {
                    "is_intent": "RANCapacity",
                    "details": {
                        "objectInstance": extracted_keywords.get("objectInstance", ""),
                        "polygon": extracted_keywords.get("polygon", ""),
                        "RAT": extracted_keywords.get("RAT", ""),
                        "DL ARFCN": extracted_keywords.get("DL ARFCN", ""),
                        "Average DL PRB Load": extracted_keywords.get("Average DL PRB Load", ""),
                        "Average UL PRB Load": extracted_keywords.get("Average UL PRB Load", ""),
                        "High DL PRB Load Ratio": extracted_keywords.get("High DL PRB Load Ratio", ""),
                        "High DL PRB Load Threshold": extracted_keywords.get("High DL PRB Load Threshold", ""),
                        "High UL PRB Load Ratio": extracted_keywords.get("High UL PRB Load Ratio", ""),
                        "High UL PRB Load Threshold": extracted_keywords.get("High UL PRB Load Threshold", "")
                    }
                }

        # 将 output_data 分段发送
        output_json = json.dumps(output_data)
        for i in range(0, len(output_json), 50):  # 每次传送 50 字符
            yield output_json[i:i+50]
            time.sleep(0.1)  # 模拟延迟

    return Response(generate_response(), mimetype='application/json')


def fill_intent_template(intent_type, keywords):
    templates = {
        "UE Throughput Intent": "Intent:\n  id: 'Intent_3'\n  userLabel: 'Radio_Network_Coverage_Performance_Assurance'\n  intentExpectation:\n    - expectationId: '1'\n      expectationVerb: 'Make_Sure'\n      expectationObjects:\n      - objectInstance: 'SubNetwork_1'\n        objectContexts:\n        - contextAttribute: 'CoverageAreaPolygon'\n          contextCondition: 'IS_ALL_OF' \n          contextValueRange: \n          - convexGeoPolygon:\n            - latitude: '{latitude1}'\n              longitude: '{longitude1}'\n            - latitude: '{latitude2}'\n              longitude: '{longitude2}'\n            - latitude: '{latitude3}'\n              longitude: '{longitude3}'\n            - latitude: '{latitude4}'\n              longitude: '{longitude4}'\n        - contextAttribute: 'DlFrequency'\n          contextCondition: 'IS_ALL_OF'\n          contextValueRange: \n          - arfcn: '{arfcn}'\n        - contextAttribute: 'RAT'\n          contextCondition: 'IS_ALL_OF'\n          contextValueRange: \n          - 'NR'\n    expectationTargets:\n      - targetName: 'MbpsaveDLRANUEThptTarget'\n        targetCondition: 'IS_GREATER_THAN'\n        targetValueRange: '{throughputTarget}'\n  intentPriority: '4'\n  observationPeriod: '60'\n  intentReportInference: 'IntentReport_3'\n",
        "RAN Capacity Intent": "Intent:\n  id: 'Intent_3'\n  userLabel: 'Radio_Network_Coverage_Performance_Assurance'\n  intentExpectation:\n    - expectationId: '1'\n      expectationVerb: 'Ensure'\n      expectationObjects:\n      - objectInstance: 'SubNetwork_1'\n        objectContexts:\n        - contextAttribute: 'CoverageAreaPolygon'\n          contextCondition: 'IS_ALL_OF' \n          contextValueRange: \n          - convexGeoPolygon:\n            - latitude: '{latitude1}'\n              longitude: '{longitude1}'\n            - latitude: '{latitude2}'\n              longitude: '{longitude2}'\n            - latitude: '{latitude3}'\n              longitude: '{longitude3}'\n            - latitude: '{latitude4}'\n              longitude: '{longitude4}'\n        - contextAttribute: 'DlFrequency'\n          contextCondition: 'IS_ALL_OF'\n          contextValueRange: \n          - arfcn: '{arfcn}'\n        - contextAttribute: 'RAT'\n          contextCondition: 'IS_ALL_OF'\n          contextValueRange: \n          - 'NR'\n    expectationTargets:\n      - targetName: 'highDlPrbLoadRatioTarget'\n        targetCondition: 'IS_LESS_THAN'\n        targetValueRange: '{highDlPrbLoadRatioTarget}'\n      - targetName: 'highDlPrbLoadRatioTarget.HighDlPrbLoad'\n        targetCondition: 'IS_GREATER_THAN'\n        targetValueRange: '{highDlPrbLoadRatioHighDlPrbLoad}'\n  intentPriority: '4'\n  observationPeriod: '60'\n  intentReportInference: 'IntentReport_3'\n",
        "Coverage Intent": "Intent:\n  id: 'Intent_3'\n  userLabel: 'Radio_Network_Coverage_Performance_Assurance'\n  intentExpectation:\n    - expectationId: '1'\n      expectationVerb: 'Ensure'\n      expectationObjects:\n      - objectInstance: 'SubNetwork_1'\n        objectContexts:\n        - contextAttribute: 'CoverageAreaPolygon'\n          contextCondition: 'IS_ALL_OF' \n          contextValueRange: \n          - convexGeoPolygon:\n            - latitude: '{latitude1}'\n              longitude: '{longitude1}'\n            - latitude: '{latitude2}'\n              longitude: '{longitude2}'\n            - latitude: '{latitude3}'\n              longitude: '{longitude3}'\n            - latitude: '{latitude4}'\n              longitude: '{longitude4}'\n        - contextAttribute: 'DlFrequency'\n          contextCondition: 'IS_ALL_OF'\n          contextValueRange: \n          - arfcn: '{arfcn}'\n        - contextAttribute: 'RAT'\n          contextCondition: 'IS_ALL_OF'\n          contextValueRange: \n          - 'NR'\n    expectationTargets:\n      - targetName: 'WeakRSRPRatio'\n        targetCondition: 'IS_LESS_THAN'\n        targetValueRange: '{weakRsrpRatio}'\n        targetContexts:\n        - contextAttribute: 'WeakRSRPThreshold'\n          contextCondition: 'IS_LESS_THAN'\n          contextValueRange: '{weakRsrpThreshold}'\n      - targetName: 'LowSINRRatio'\n        targetCondition: 'IS_LESS_THAN'\n        targetValueRange: '{lowSinrRatio}'\n        targetContexts:\n        - contextAttribute: 'LowSINRThreshold'\n          contextCondition: 'IS_LESS_THAN'\n          contextValueRange: '{lowSinrThreshold}'\n  intentPriority: '4'\n  observationPeriod: '60'\n  intentReportInference: 'IntentReport_3'\n",
    }

    if intent_type in templates:
        template = templates[intent_type]

        polygon_str = keywords.get('polygon', '').replace('(', '').replace(')', '').replace(' ', '')
        coordinates = polygon_str.split(',')

        filled_intent = template.format(
            latitude1=coordinates[0], 
            longitude1=coordinates[1],
            latitude2=coordinates[2], 
            longitude2=coordinates[3],
            latitude3=coordinates[4], 
            longitude3=coordinates[5],
            latitude4=coordinates[6], 
            longitude4=coordinates[7],
            arfcn=keywords.get('DL ARFCN', ''),
            RAT=keywords.get('RAT', '').strip("'"),
            throughputTarget=keywords.get('MbpsaveDLRANUEThptTarget', ''),
            highDlPrbLoadRatioTarget=keywords.get('highDlPrbLoadRatioTarget', ''),
            highDlPrbLoadRatioHighDlPrbLoad=keywords.get('highDlPrbLoadRatioTarget.HighDlPrbLoad', ''),
            weakRsrpRatio=keywords.get('Weak RSRP ratio', ''),
            weakRsrpThreshold=keywords.get('Weak RSRP threshold', ''),
            lowSinrRatio=keywords.get('Low SINR ratio', ''),
            lowSinrThreshold=keywords.get('Low SINR threshold', '')
        )

        return filled_intent
    else:
        return "Unknown Intent Type"

@app.route("/convert_to_3gpp_format/", methods=["POST"])
def convert_to_3gpp_format():
    input_data = request.json
    intent_type = determine_intent_type(input_data)
    filled_intent = fill_intent_template(intent_type, input_data)
    return jsonify({"response": filled_intent})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

