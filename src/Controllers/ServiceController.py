import io
import json
import datetime as dt
from flask import Flask, request, send_file, jsonify
from src.Controllers import RPCClient
from src.daolayer import MongoReadWrite
from src.GENAI.EvaluationAsync import EvaluationAsync
from src.GENAI.DataGenerator import router as DGrouter
from src.GENAI.Controller import router as ControllerRouter
from src.GENAI.EvaluationController import router as EvaluationControllerRouter
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
CORS(DGrouter, resources={r"/data-gen/*": {"origins": "http://localhost:3000"}})
CORS(ControllerRouter, resources={r"/controller/*": {"origins": "http://localhost:3000"}})
CORS(EvaluationControllerRouter, resources={r"/evaluation-controller/*": {"origins": "http://localhost:3000"}})

app.register_blueprint(DGrouter, url_prefix='/data-gen')
app.register_blueprint(ControllerRouter, url_prefix='/controller')
app.register_blueprint(EvaluationControllerRouter, url_prefix='/evaluation-controller')


mongo_obj = MongoReadWrite.mongoReadWrite()

def form_response_ack(corrid):
    data = {'jobId': corrid, 'startTime': dt.datetime.now().isoformat(), 'status': "STARTED"}
    json_data = json.dumps(data)
    return json_data

@app.route('/gen_ai_evaluation', methods=['POST'])
def gen_ai_evaluation():
    content = json.dumps(request.json)
    corr_id = rpcClient.send_request(content)
    resp_ack = form_response_ack(corr_id)
    return resp_ack

@app.route('/downloadEvaluationData', methods=['GET'])
def downloadEvaluationData():
    try:
        evaluation_detail = mongo_obj.read_single_data_with_filter('evaluation', request.json['jobId'],
                                                                   'jobId')
        if evaluation_detail['executionStatus'] == 'Failed':
            data = {'jobId': request.json['jobId'], 'status': "Failed",
                    'statusMessage': evaluation_detail['errorMessage']}
            json_data = json.dumps(data)
            return json_data
        elif evaluation_detail['executionStatus'] == 'Inprogress':
            data = {'jobId': request.json['jobId'], 'status': "Inprogress",
                    'statusMessage': evaluation_detail['errorMessage']}
            json_data = json.dumps(data)
            return json_data
        evaluation_obj = EvaluationAsync()
        evaluation_output_df = evaluation_obj.download_evaluation_data(request.json)
        excel_output = io.BytesIO()
        evaluation_output_df.to_excel(excel_output, index=False)
        excel_output.seek(0)
        return send_file(
            excel_output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'{request.json["jobId"]}_Evaluation_output.xlsx'
        )
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    rpcClient = RPCClient.RpcClient("rpcQueue")
    app.run(host='0.0.0.0',port=5000)

