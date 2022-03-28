# Copyright (C) LA Sistemas - All Rights Reserved.
#
# Written by Leonardo - ledharaujo@gmail.com, February 2022.
#
# Unauthorized copying of this file, via any medium, is strictly prohibited.
# Proprietary and confidential.


# External modules
import os
import hashlib
from functools import wraps
from sqlalchemy import update
from dotenv import load_dotenv
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from flask import Flask, request, render_template, redirect, url_for, session


# Init dotenv
load_dotenv()

# Constants
DATABASE_URL = os.getenv('DATABASE_URL').replace('postgres', 'postgresql')

# Init flask
app = Flask(__name__, static_folder='assets')

# Config session
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

# Config DB
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Class model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=False, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, unique=False, nullable=False)
    is_active = db.Column(db.Integer, unique=False, nullable=False)
    is_admin = db.Column(db.Integer, unique=False, nullable=False)
    is_first_access = db.Column(db.Integer, unique=False, nullable=False)

    def __init__(self, name, email, password, is_active, is_admin, is_first_access):
        self.name = name
        self.email = email
        self.password = password
        self.is_active = is_active
        self.is_admin = is_admin
        self.is_first_access = is_first_access


class Prs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String, unique=False, nullable=False)
    revisor = db.Column(db.String, unique=False, nullable=False)
    link = db.Column(db.String, unique=True, nullable=False)
    status = db.Column(db.Integer, unique=False, nullable=False)

    def __init__(self, author, revisor, link, status):
        self.author = author
        self.revisor = revisor
        self.link = link
        self.status = status

# Encrypt pass
def encrypt_string(hash_string):
    '''Function for encrypt password.'''

    return hashlib.sha256(hash_string.strip().encode()).hexdigest()

# Decorators
def require_auth(f):
    @wraps(f)
    def slave(*args, **kwargs):
        if not session.get('email'):
            return redirect('/login')

        return f(*args, **kwargs)

    return slave

def require_admin_auth(f):
    @wraps(f)
    def slave(*args, **kwargs):
        if not session.get('admin') or session.get('admin') != 1:
            return redirect('/')

        return f(*args, **kwargs)

    return slave

def require_reset_password(f):
    @wraps(f)
    def slave(*args, **kwargs):
        if session.get('is_first_access') == 1:
            return redirect('/reset')

        return f(*args, **kwargs)

    return slave

# Public routes
@app.route('/login')
def login():
    '''Function login.'''

    return render_template('login.html')

@app.route('/auth', methods=['POST'])
def auth():
    '''Function to auth user.'''

    if request.form['email'] != '' and request.form['password'] != '':
        if not (user := Users.query.filter_by(email=request.form['email']).first()):
            print('Error: user not found.')

            return redirect('/login')

        if user.password != encrypt_string(request.form['password']):
            print('Error: email or password incorrect.')

            return redirect('/login')

        if not user.is_active:
            print('Error: user inactive.')

            return redirect('/login')

        session['id'] = user.id
        session['email'] = user.email
        session['admin'] = user.is_admin
        session['is_first_access'] = user.is_first_access

        return redirect('/')

# Private routes
@app.route('/reset')
@require_auth
def first_access():
    '''Function reset pass first access.'''

    return render_template('first-access.html')

@app.route('/reset-pass-user', methods=['POST'])
@require_auth
def reset_pass_user():
    '''Function reset password user.'''

    if not session.get('id'):
        return redirect('/reset')

    try:
        if not (user := Users.query.get(session.get('id'))):
            return redirect('/reset')

        user.password = encrypt_string(request.form['pass'])
        user.is_first_access = 0

        db.session.commit()

    except SQLAlchemyError as err:
        db.session.rollback()

        return redirect('/reset')

    session['is_first_access'] = 0

    return redirect('/')

@app.route('/logout')
@require_auth
def logout():
    '''Function to logout.'''

    session.pop('id', default=None)
    session.pop('email', default=None)
    session.pop('admin', default=None)
    session.pop('is_first_login', default=None)

    return redirect('/login')

@app.route('/')
@require_auth
@require_reset_password
def index():
    '''Function index.'''

    try:
        prs = Prs.query.all()

    except SQLAlchemyError as err:
        print('Error', err)

        return

    return render_template('index.html', prs=prs, session=session)

@app.route('/users')
@require_auth
@require_admin_auth
@require_reset_password
def users():
    '''Function users.'''

    try:
        users = Users.query.all()

    except SQLAlchemyError as err:
        print('Error', err)

        return

    return render_template('users.html', users=users)

@app.route('/users-deactive')
@require_auth
@require_admin_auth
@require_reset_password
def users_deactive():
    '''Function deactive users.'''

    try:
        users = Users.query.all()

    except SQLAlchemyError as err:
        print('Error: ', err)

        return

    return render_template('users-deactive.html', users=users)

# CRUD
@app.route('/create-pr', methods=['POST'])
@require_auth
def create_pr():
    '''Function create pull request.'''

    rep = {}
    due = []

    due.append('autor')
    due.append('revisor')
    due.append('link')
    due.append('situacao')

    for key in request.form.keys():
        if key not in due:
            rep['status'] = 400
            rep['message'] = f'Error: key {key} not found.'

            return rep

    try:
        args = {}

        args['author'] = request.form['autor']
        args['revisor'] = request.form['revisor']
        args['link'] = request.form['link']
        args['status'] = request.form['situacao']

        pr = Prs(**args)

        db.session.add(pr)
        db.session.commit()

    except SQLAlchemyError as err:
        db.session.rollback()

        rep['status'] = 400
        rep['message'] = err

        return rep

    rep['status'] = 200
    rep['message'] = f'PR criado com sucesso.'

    return rep

@app.route('/update-pr', methods=['POST'])
@require_auth
def update_pr():
    '''Function update pull request.'''

    rep = {}
    due = []

    due.append('id')
    due.append('autor')
    due.append('revisor')
    due.append('link')
    due.append('situacao')

    for key in request.form.keys():
        if key not in due:
            rep['status'] = 400
            rep['message'] = f'Error: key {key} not found.'

            return rep

    try:
        if not (pr := Prs.query.get(request.form['id'])):
            rep['status'] = 400
            rep['message'] = f'Error: PR not found.'

            return rep

        pr.author = request.form['autor']
        pr.revisor = request.form['revisor']
        pr.link = request.form['link']
        pr.status = request.form['situacao']

        db.session.commit()

    except SQLAlchemyError as err:
        db.session.rollback()

        rep['status'] = 400
        rep['message'] = err

        return rep

    rep['status'] = 200
    rep['message'] = f'PR alterado com sucesso.'

    return rep

@app.route('/delete-pr/<int:id>', methods=['DELETE'])
@require_auth
def delete_pr(id):
    '''Function delete pull request.'''

    rep = {}

    if not id:
        rep['status'] = 400
        rep['message'] = f'Error: id not found.'

        return rep

    try:
        if not (pr := Prs.query.get(id)):
            rep['status'] = 400
            rep['message'] = f'Error: PR not found.'

            return rep

        db.session.delete(pr)
        db.session.commit()

    except SQLAlchemyError as err:
        db.session.rollback()

        rep['status'] = 400
        rep['message'] = err

        return rep

    rep['status'] = 200
    rep['message'] = f'PR deletado com sucesso.'

    return rep

@app.route('/create-user', methods=['POST'])
@require_auth
@require_admin_auth
def create_user():
    '''Function create user.'''

    rep = {}
    due = []

    due.append('name')
    due.append('email')
    due.append('pass')
    due.append('profile')

    for key in request.form.keys():
        if key not in due:
            rep['status'] = 400
            rep['message'] = f'Error: key {key} not found.'

            return rep

    try:
        if not (user := Users.query.filter_by(email=request.form['email']).first()):
            args = {}

            args['name'] = request.form['name']
            args['email'] = request.form['email']
            args['is_active'] = 1
            args['is_first_access'] = 1
            args['password'] = encrypt_string(request.form['pass'])
            args['is_admin'] = request.form['profile']

            user = Users(**args)

            db.session.add(user)
            db.session.commit()

            rep['status'] = 200
            rep['message'] = f'Usuário criado com sucesso.'

            return rep

    except SQLAlchemyError as err:
        db.session.rollback()

        rep['status'] = 400
        rep['message'] = err

        return rep

    rep['status'] = 400
    rep['message'] = f'Error: user already exists.'

    return rep

@app.route('/update-user', methods=['POST'])
@require_auth
@require_admin_auth
def update_user():
    '''Function update user.'''

    rep = {}
    due = []

    due.append('id')
    due.append('name')
    due.append('email')
    due.append('pass')
    due.append('profile')

    for key in request.form.keys():
        if key not in due:
            rep['status'] = 400
            rep['message'] = f'Error: key {key} not found.'

            return rep

    try:
        if not (user := Users.query.get(request.form['id'])):
            rep['status'] = 400
            rep['message'] = f'Error: user not found.'

            return rep

        user.name = request.form['name']
        user.email = request.form['email']
        user.password = '' if request.form['pass'] == '' else encrypt_string(request.form['pass'])
        user.is_admin = request.form['profile']

        if request.form['pass'] != '':
            user.is_first_access = 1

        db.session.commit()

    except SQLAlchemyError as err:
        db.session.rollback()

        rep['status'] = 400
        rep['message'] = err

        return rep

    rep['status'] = 200
    rep['message'] = f'Usuário alterado com sucesso.'

    return rep

@app.route('/reactivate-user/<int:id>', methods=['POST'])
@require_auth
@require_admin_auth
def reactivate_user(id):
    '''Function reactivate user.'''

    rep = {}

    if not id:
        rep['status'] = 400
        rep['message'] = f'Error: id not found.'

        return rep

    try:
        if not (user := Users.query.get(id)):
            rep['status'] = 400
            rep['message'] = f'Error: user not found.'

            return rep

        user.is_active = 1

        db.session.commit()

    except SQLAlchemyError as err:
        db.session.rollback()

        rep['status'] = 400
        rep['message'] = err

        return rep

    rep['status'] = 200
    rep['message'] = f'Usuário reativado com sucesso.'

    return rep


@app.route('/delete-user/<int:id>', methods=['DELETE'])
@require_auth
@require_admin_auth
def delete_user(id):
    '''Function delete user.'''

    rep = {}

    if not id:
        rep['status'] = 400
        rep['message'] = f'Error: id not found.'

        return rep

    try:
        if not (user := Users.query.get(id)):
            rep['status'] = 400
            rep['message'] = f'Error: user not found.'

            return rep

        user.is_active = 0

        db.session.commit()

    except SQLAlchemyError as err:
        db.session.rollback()

        rep['status'] = 400
        rep['message'] = err

        return rep

    rep['status'] = 200
    rep['message'] = f'Usuário deletado com sucesso.'

    return rep

# Run app
if __name__ == '__main__':
    # db.create_all()
    app.run()

