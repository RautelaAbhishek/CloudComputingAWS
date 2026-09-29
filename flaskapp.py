from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3
import os
app = Flask(__name__)

DB = '/var/www/html/flaskapp/users.db'
UPLOAD_FOLDER = '/var/www/html/flaskapp/uploads'

conn = sqlite3.connect(DB)
conn.execute('''CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  firstname TEXT NOT NULL,
  lastname TEXT NOT NULL,
  email TEXT NOT NULL,
  address TEXT NOT NULL,
  filename TEXT,
  word_count INTEGER)''')
conn.commit()
conn.close()

def get_user(username):
  conn = sqlite3.connect(DB)
  conn.row_factory = sqlite3.Row
  user = conn.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
  conn.close()
  return user

@app.route('/')
def index():
  return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
  username = request.form['username']
  if get_user(username):
    return render_template('register.html', error='Username already exists')

  filename = None
  word_count = None
  file = request.files.get('file')
  if file and file.filename:
    filename = secure_filename(username + '_' + file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)
    word_count = len(open(path).read().split())

  conn = sqlite3.connect(DB)
  conn.execute('INSERT INTO users (username, password, firstname, lastname, email, address, filename, word_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
    (username, request.form['password'], request.form['firstname'], request.form['lastname'],
     request.form['email'], request.form['address'], filename, word_count))
  conn.commit()
  conn.close()
  return redirect(url_for('profile', username=username))

@app.route('/profile/<username>')
def profile(username):
  user = get_user(username)
  if user is None:
    return redirect(url_for('login'))
  return render_template('profile.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    user = get_user(request.form['username'])
    if user and user['password'] == request.form['password']:
      return redirect(url_for('profile', username=user['username']))
    return render_template('login.html', error='Invalid username or password')
  return render_template('login.html')

@app.route('/download/<filename>')
def download(filename):
  return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
  app.run()
