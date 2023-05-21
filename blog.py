from logging import debug
from os import environ, urandom
from flask import Flask, redirect, render_template, g, request, session, url_for, Blueprint, flash

import sqlite3 as sqli
import flask

from werkzeug.utils import escape
from werkzeug.security import check_password_hash, generate_password_hash




app = Flask(__name__)


app.secret_key = urandom(12)



con = sqli.connect('blog.db')
cur = con.cursor()


cur.execute("CREATE TABLE IF NOT EXISTS posts(id INTEGER PRIMARY KEY AUTOINCREMENT NULL, title TEXT NULL, content TEXT NULL, published TEXT NULL, author TEXT NULL)")

cur.execute("CREATE TABLE IF NOT EXISTS user(id INTEGER PRIMARY KEY AUTOINCREMENT NULL, username VARCHAR(50) NULL, author VARCHAR(50), password VARCHAR(20) NULL, FOREIGN KEY(author) REFERENCES posts(author))")
con.commit()



@app.route('/', methods = ['POST', 'GET'])
def home():

    return render_template('home.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    con = sqli.connect('blog.db')
    cur = con.cursor()
    if request.method == 'GET':
        return render_template('register.html')

    if request.method == 'POST':
        username = request.form['username']
        author = request.form['author']
        password = request.form['password']

        cur.execute('INSERT OR IGNORE INTO user VALUES(?,?,?,?)',(None, username, author, password))
        con.commit()
        return redirect(url_for('login'))

    return redirect(url_for('login'))
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    con = sqli.connect('blog.db')
    cur = con.cursor()
    if request.method == 'GET':
       return render_template('login.html')
    error = None
    if request.method == 'POST':
    
        con = sqli.connect('blog.db')
        cur = con.cursor()

        username = request.form['username']
        author = cur.execute('SELECT author FROM user WHERE username = ?', (username,)).fetchone()
        password = cur.execute('SELECT password FROM user WHERE username = ?', (username,)).fetchone()
        session['username'] = username
        session['author'] = author
        error = None
        user = cur.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        session['password'] = password
        session['author'] = author


        if user is None:
            error = 'Incorrect username.'
        elif not session['password']:
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session[2] = user[0]
            return redirect(url_for('dashboard'))

        flash(error)
    return redirect(url_for('home', session))


@app.route('/new_post', methods = ['GET', 'POST'])
def new_post():
    con = sqli.connect('blog.db')
    cur = con.cursor()
    


    if request.method == 'GET':
        cookie =request.cookies.get('SecureCookieSession')
        return render_template('new_post.html')
    
    if request.method == 'POST':
        author = session.get('author')
        date = str(request.form['date'])
        session['author'] = author
        title = request.form['title']
        post = request.form['post']
        cur.execute('INSERT OR IGNORE INTO posts VALUES(?,?,?,?,?)', (None, title, post, date, author ))
        con.commit()        
        
        return redirect(url_for('dashboard'))

    return redirect(url_for('dashboard'))    

@app.route('/dashboard', methods=['GET'])
def dashboard():
    con = sqli.connect('blog.db')
    cur = con.cursor()
    
    if request.method == 'GET':
        fetch = cur.execute('SELECT * FROM posts').fetchall()

    return render_template('dashboard.html', posts=fetch)

@app.route('/post/<id>', methods=['GET', 'POST'])
def post(id):
    con = sqli.connect('blog.db')
    cur = con.cursor()
    fetch = cur.execute('SELECT * FROM posts WHERE (id = ?)', (id,)).fetchone()

    return render_template('post.html', fetch=fetch)

@app.route('/post/<id>/edit', methods=['GET', 'POST'])
def edit(id):
    con = sqli.connect('blog.db')
    cur = con.cursor()
    if request.method == 'GET':
        fetch = cur.execute('SELECT * FROM posts WHERE (id = ?)', (id,)).fetchone()
        return render_template('update_post.html', fetch = fetch)

    if request.method == 'POST':
        post_update = request.form['post']
        update = cur.execute('UPDATE posts SET content = ? WHERE (id = ?)', (post_update, id)).fetchone()
        con.commit()
        return redirect(url_for('dashboard'))
    return redirect(url_for('dashboard'))

@app.route('/post/<id>/delete', methods =['POST'])
def delete(id):
    con = sqli.connect('blog.db')
    cur = con.cursor()

    if request.method == 'POST':
        cur.execute('DELETE FROM posts WHERE id = ?', (id,)).fetchone()
        con.commit()

        
        return redirect(url_for('dashboard'))
    return redirect(url_for('dashboard'))

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('home'))
if __name__ == '__main__':
    app.run(debug=True)
