from flask import Flask, render_template, request, redirect
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect('/checker')
    return render_template('login.html')

@app.route('/checker', methods=['GET', 'POST'])
def checker():
    if request.method == 'POST':
        text1 = request.form['text1']
        text2 = request.form['text2']
        code1 = request.form['code1']
        code2 = request.form['code2']

        # TEXT similarity
        tfidf = TfidfVectorizer()
        text_vectors = tfidf.fit_transform([text1, text2])
        text_similarity = cosine_similarity(text_vectors[0:1], text_vectors[1:2])[0][0]

        # CODE similarity
        code_vectors = tfidf.fit_transform([code1, code2])
        code_similarity = cosine_similarity(code_vectors[0:1], code_vectors[1:2])[0][0]

        text_percent = round(text_similarity * 100, 2)
        code_percent = round(code_similarity * 100, 2)

        return render_template('result.html',
                               text_result=text_percent,
                               code_result=code_percent)

    return render_template('checker.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)