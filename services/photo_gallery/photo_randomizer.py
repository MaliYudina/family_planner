from flask import Flask, jsonify, render_template
import sqlite3
import random

app = Flask(__name__)

def get_random_photo_url():
    conn = sqlite3.connect('photo_gallery.db')
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM photos ORDER BY RANDOM() LIMIT 1")
    url = cursor.fetchone()
    conn.close()
    return url[0] if url else None

@app.route('/')
def home():
    photo_url = get_random_photo_url()
    return render_template('index.html', photo_url=photo_url)

if __name__ == '__main__':
    app.run(debug=True)
