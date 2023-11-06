from flask import Flask, render_template, request, jsonify

import sys
sys.path.append('../main/')
from TQLRunnerT5 import TQLRunner

app = Flask(__name__)

# @app.route('/')
# def home():
#     return render_template('index.html')

@app.route('/api/data', methods=['POST'])
def process_text():
    schema = request.json.get("schema", "")
    query = request.json.get("query", "").strip()
        
    processed_text = ''
    try:    
        tqlRunner = TQLRunner(schema)
        processed_text = tqlRunner.get_SQL_query(query)
    except Exception as e:
        return jsonify({"final_SQL_query" : f'Query processing Failed with error message {e}'}), 200, {"Content-type" : "application/json"}
    
    return jsonify({"final_SQL_query" : processed_text}), 200, {"Content-type" : "application/json"}

if __name__ == '__main__':
    app.run(host = 'localhost', port = '5000', debug=False)