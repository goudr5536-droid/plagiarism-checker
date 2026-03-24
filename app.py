from flask import Flask, render_template, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pypdf import PdfReader
import os

app = Flask(__name__)

# ---------- PREPROCESS ----------
def preprocess(text):
    return text.lower().strip()

# ---------- HIGHLIGHT ----------
def highlight(text1, text2):
    words1 = set(text1.split())
    words2 = set(text2.split())
    common = words1.intersection(words2)

    def mark(text):
        return " ".join([f"<mark>{w}</mark>" if w in common else w for w in text.split()])

    return mark(text1), mark(text2)
#----------- READ FILE ------------#
from pypdf import PdfReader

def read_file(file):
    if file.filename.endswith('.txt'):
        return file.read().decode('utf-8', errors='ignore')

    elif file.filename.endswith('.pdf'):
        try:
            reader = PdfReader(file)
            text = ""

            for page in reader.pages:
                content = page.extract_text()
                if content:
                    text += content

            if text.strip() == "":
                return "PDF has no readable text"

            return text

        except:
            return "Error reading PDF"

    else:
        return ""


# ---------- LANGUAGE DETECTION ----------
def detect_language(code):
    code = code.lower()

    if "public static void main" in code:
        return "Java"
    elif "#include" in code:
        return "C"
    elif "cout" in code:
        return "C++"
    elif "def " in code:
        return "Python"
    elif "console.log" in code:
        return "JavaScript"
    else:
        return "Text"

# ---------- REWRITE ----------
def rewrite(text):
    words = text.split()
    return " ".join(words[::-1])

# ---------- ROUTES ----------

@app.route('/')
def home():
    return render_template("login.html")


@app.route('/checker', methods=['GET', 'POST'])
def checker():

    if request.method == 'POST':

        text1 = request.form.get('text1', '')
        text2 = request.form.get('text2', '')
        rewrite_text = request.form.get('rewrite', '')

        file1 = request.files.get('file1')
        file2 = request.files.get('file2')

        if file1 and file1.filename:
            text1 = read_file(file1)

        if file2 and file2.filename:
            text2 = read_file(file2)

        if not text1.strip() or not text2.strip():
            return "Please enter both texts"

        t1 = preprocess(text1)
        t2 = preprocess(text2)

        tfidf = TfidfVectorizer(stop_words="english")
        vectors = tfidf.fit_transform([t1, t2])
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        percent = round(similarity * 100, 2)

        h1, h2 = highlight(text1, text2)

        lang1 = detect_language(text1)
        lang2 = detect_language(text2)

        rewritten = rewrite(rewrite_text) if rewrite_text else ""

        return render_template("result.html",
                               result=percent,
                               text1=h1,
                               text2=h2,
                               lang1=lang1,
                               lang2=lang2,
                               rewritten=rewritten)

    return render_template("checker.html")


# ---------- RUN ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)