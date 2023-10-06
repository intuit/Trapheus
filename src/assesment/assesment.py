from flask import Flask, render_template, request, jsonify
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
import nltk
nltk.download('punkt')

app = Flask(__name__)
# @app.route('/')
# def index():
#     return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            df = pd.read_csv(file)

            # replace column name
            text = ' '.join(df['(df[0])'])

            # Basic NLP assessment
            tokens = word_tokenize(text)
            fdist = FreqDist(tokens)
            most_common_words = fdist.most_common(10)

            return jsonify(results=f"Most common words: {most_common_words}")
        
        else:
            return jsonify(error="Invalid file format. Please upload a CSV file.")
    except Exception as e:
        return jsonify(error = str(e))
    
if __name__ == '__main__':
    app.run(debug=True)