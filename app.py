from flask import Flask, request, session, redirect, url_for, render_template, flash
import psycopg2 
import psycopg2.extras
import re 
import os
from werkzeug.security import generate_password_hash, check_password_hash
 
app = Flask(__name__)
app.secret_key = 'contraseña'

from werkzeug.middleware.proxy_fix import ProxyFix

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

params = {
    'dbname': 'flask_db',
    'user': os.environ['DB_USERNAME'],
    'password': os.environ['DB_PASSWORD'],
    'host': '10.0.0.4'
}
 
conn = psycopg2.connect(**params)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/')
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))
 
@app.route('/login/', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
 
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))

        account = cursor.fetchone()
 
        if account:
            password_rs = account['password']
            print(password_rs)

            if check_password_hash(password_rs, password):
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                return redirect(url_for('home'))
            else:
                flash('Usuario y/o contraseña incorrectos')
        else:
            flash('Usuario y/o contraseña incorrectos')
 
    return render_template('login.html')
  
@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:

        username = request.form['username']
        password = request.form['password']
        
        _hashed_password = generate_password_hash(password)
 

        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        print(account)

        if account:
            flash('Cuenta ya existente')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Nombre de usuario solo debe contener letras y números')
        elif not username or not password:
            flash('Completa el registro')
        else:
            
            cursor.execute("INSERT INTO users (username, password) VALUES (%s,%s)", (username, _hashed_password))
            conn.commit()
            flash('Registrado correctamente')
    elif request.method == 'POST':
    
        flash('Completa el registro')
    
    return render_template('register.html')
   
   
@app.route('/logout')
def logout():
    
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   
   return redirect(url_for('login'))
  
@app.route('/profile')
def profile(): 
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
   
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        
        return render_template('profile.html', account=account)
    
    return redirect(url_for('login'))
