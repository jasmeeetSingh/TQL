from flask import Flask, render_template, request

import sys
sys.path.append('../main/')
from TQLRunner import TQLRunner

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/set_schema', methods=['POST'])
def process_text():
    schema = request.form['user_text'].strip()
    query = request.form['user_text1'].strip()
        
    processed_text = ''
    try:    
        tqlRunner = TQLRunner(schema)
        processed_text = tqlRunner.get_SQL_query(query)
    except:
        return render_template('failure.html', actual_text = query)
    
    return render_template('results.html', processed_text=processed_text, actual_text = query)

if __name__ == '__main__':
    app.run(debug=True)