import json
from flask import jsonify,Blueprint
from src.daolayer import MongoReadWrite

mongo_obj = MongoReadWrite.mongoReadWrite()

router = Blueprint(
    'evaluation-controller', __name__, )

def load_metrics_config(config_file='C:\gen_ai_asuurance_2078155\qea-gen-ai-assurance\metrices_config.json'):
    with open(config_file, 'r') as file:
        config = json.load(file)
    return config.get('metrics', {})

@router.route('/metrics_config', methods=['GET'])
def get_metrics():
    try:
        metrics = load_metrics_config()
        return jsonify({'metrics': metrics})
    except Exception as e:
        return jsonify({"error": str(e)}), 500