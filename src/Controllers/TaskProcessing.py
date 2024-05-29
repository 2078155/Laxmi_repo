import json
from src.GENAI.EvaluationAsync import EvaluationAsync


class TaskProcessing:
    def safe_deserialize(self, input_value, jobID):
        try:
            loaded_data = json.loads(input_value)
            loaded_data['jobID'] = jobID
            return loaded_data
        except json.JSONDecodeError as e:
            print("JSON decoding error:", e)
            return None

    def process_task(self, input_json, jobID):
        input_value = (input_json.decode("utf-8"))
        input_param = self.safe_deserialize(input_value, jobID)
        if input_param is not None:
            try:
                if 'executionType' in input_param:
                    evaluation_obj = EvaluationAsync()
                    return evaluation_obj.evaluation_calculation(input_param)
            except Exception as e:
                import sys
                print('Error in Task processing: ', str(e), sys.exc_info()[-1].tb_lineno)
                return {"resultStatus": "ERROR", "resultMessage": str(e)}
