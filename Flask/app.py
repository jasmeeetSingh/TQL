from flask import Flask, render_template, request

import sys
sys.path.append('../main/')
from TQLRunner import TQLRunner

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process_text', methods=['POST'])
def process_text():
    user_text = request.form['user_text']
    processed_text = process_user_text(user_text)
    processed_transcript = process_user_transcript(user_text)
    return render_template('results.html', processed_text=processed_text, table_html=processed_transcript)

def process_user_text(user_text):
    
    from transformers import PegasusForConditionalGeneration, PegasusTokenizer, SummarizationPipeline

    model_name = "renegarza/PegasusMedicalSummary"
    tokenizer = PegasusTokenizer.from_pretrained(model_name)
    model = PegasusForConditionalGeneration.from_pretrained(model_name)

    summarizer = SummarizationPipeline(model=model, tokenizer=tokenizer, device = 0)

    summary = summarizer(user_text)
    return summary[0]['summary_text']

def process_user_transcript(user_text):
        
    df = get_table(user_text)
    table_html = df.to_html(index = False, justify = 'left')
    
    return table_html

if __name__ == '__main__':
    app.run(debug=True)