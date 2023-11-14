from flask import Flask, render_template, request, jsonify, session
import pandas as pd

import sys
sys.path.append('../main/')
from TQLRunnerSQLCoder import TQLRunner

app = Flask(__name__)

# @app.route('/')
# def home():
#     return render_template('index.html')

@app.route('/api/data', methods=['POST'])
def process_text():
    global tqlRunner
    schema = request.json.get("schema", "")
    query = request.json.get("query", "").strip()
    df = pd.DataFrame.from_dict(eval(request.json.get("dataframe", "")))
    print(df)
        
    processed_text = ''
    try:    
        # tqlRunner = session.get('tqlRunner')
        if(schema != "Excel Upload"):
            tqlRunner.set_schema(schema)
        else:
            tqlRunner.set_schema(schema, df)
        processed_text = tqlRunner.get_SQL_query(query)
    except Exception as e:
        return jsonify({"final_SQL_query" : f'Query processing Failed with error message {e}'}), 200, {"Content-type" : "application/json"}
    
    return jsonify({"final_SQL_query" : processed_text}), 200, {"Content-type" : "application/json"}

tqlRunner = TQLRunner()

if __name__ == '__main__':
    app.run(host = 'localhost', port = '5000', debug=False)
    