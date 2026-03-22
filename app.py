from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
import nltk
from nltk.tokenize import word_tokenize
import langdetect
import os

# Download NLTK punkt tokenizer if not already
nltk.download('punkt')

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database setup
conn = sqlite3.connect('plagiarism.db', check_same_thread=False)
c = conn.cursor()

# Users table
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
''')

# Submissions table
c.execute('''
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT,
    user_id INTEGER,
    language TEXT,
    similarity REAL
)
''')
conn.commit()

# Tokenized TF-IDF similarity
def calculate_similarity(text1, text2):
    # Tokenize both texts
    tokens1 = word_tokenize(text1)
    tokens2 = word_tokenize(text2)
    # Join tokens back as string for TF-IDF
    joined1 = " ".join(tokens1)
    joined2 = " ".join(tokens2)
    # TF-IDF vectors
    vectorizer = TfidfVectorizer().fit([joined1, joined2])
    vectors = vectorizer.transform([joined1, joined2])
    sim_score = cosine_similarity(vectors[0], vectors[1])
    return sim_score[0][0]

# Routes
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']
    c.execute("SELECT * FROM users WHERE username="sreeja" AND password="1234"", (username, password))
    user = c.fetchone()
    if user:
        session['user_id'] = user[0]
        return redirect(url_for('checker'))
    else:
        return "Invalid credentials! <a href='/'>Try again</a>"

@app.route('/checker')
def checker():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('checker.html')

@app.route('/check', methods=['POST'])
def check():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    content = request.form['content']
    user_id = session['user_id']

    # Language detection
    try:
        language = langdetect.detect(content)
    except:
        language = 'unknown'

    # Compare with previous submissions
    c.execute("SELECT content FROM submissions")
    rows = c.fetchall()
    max_similarity = 0
    for row in rows:
        sim = calculate_similarity(content, row[0])
        if sim > max_similarity:
            max_similarity = sim

    # Save submission
    c.execute("INSERT INTO submissions (content, user_id, language, similarity) VALUES (?, ?, ?, ?)",
              (content, user_id, language, max_similarity))
    conn.commit()

    # Progress bar color
    if max_similarity < 0.3:
        color = "green"
    elif max_similarity < 0.7:
        color = "orange"
    else:
        color = "red"

    return jsonify({
        "similarity": round(max_similarity*100, 2),
        "color": color,
        "language": language
    })

@app.route('/result')
def result():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    c.execute("SELECT content, similarity, language FROM submissions WHERE user_id=? ORDER BY id DESC", (session['user_id'],))
    submissions = c.fetchall()
    return render_template('result.html', submissions=submissions)

if __name__ == '__main__':
    port=int(os.environ.get("PORT",10000))
    app.run(host='0.0.0.0, port=port')