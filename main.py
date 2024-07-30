from flask import Flask, render_template,request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_mail import Mail
from flask import redirect
import os
import json
from flask import session
import  ssl,smtplib
from logging import FileHandler, WARNING
import math

# context = ssl.SSLContext(ssl.PROTOCOL_TLS)
try:
    with open('config.json', 'r') as c:
        parameters = json.load(c)["parameters"]
except (FileNotFoundError, json.JSONDecodeError, KeyError):
    # Handle errors loading the JSON file or extracting parameters
    parameters = {
        'local_server': True,
        'local_uri': 'mysql://root:@localhost/clean code',
        'production_uri': 'mysql://root:@localhost/clean code',
        'fb_url': 'https://facebook.com/cleancode',
        'gh_url': 'https://github.com/cleancode',
        'tweet_url': 'https://x.com/cleancode',
        'gmail-user': 'padmanabhakulkarni90@gmail.com',
        'gmail-password': 'jyxv mxnu jxam nkdf',
        "recipients": "muralidharkulkarni90@gmail.com",
        "no_of_posts": 5,
        "login_image": "login.jpg",
        "admin_user": "padmanabha",
        "admin_password": "12345678",
        "upload_location": "C:\\Users\\padmanabha kulkarni\\PycharmProjects\\pythonProject16\\static"
    }

local_server = True
# app = Flask(__name__, template_folder = 'template')
app = Flask(__name__)
file_handler = FileHandler('errorlog.txt')
file_handler.setLevel(WARNING)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = parameters['upload_location']
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,  # Corrected: Integer, not a string
    MAIL_USE_SSL=True,  # Corrected: Boolean, not a string
    MAIL_USERNAME=parameters['gmail-user'],
    MAIL_PASSWORD=parameters['gmail-password']
)

mail=Mail(app)
if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = parameters['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = parameters['production_uri']

db = SQLAlchemy(app)
class Contacts(db.Model):
    slno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    phone_no = db.Column(db.String(15))
    message = db.Column(db.String(150), nullable=False)
    date = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(20), nullable=False)

class Posts(db.Model):
    slno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(30))
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(20), nullable=True)
    img_file = db.Column(db.String(20), nullable=True)



@app.route("/")
def home(posts=Posts):
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts) / int(parameters['no_of_posts']))
    # [0: params['no_of_posts']]
    # posts = posts[]
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page - 1) * int(parameters['no_of_posts']): (page - 1) * int(parameters['no_of_posts']) + int(
        parameters['no_of_posts'])]
    # Pagination Logic
    # First
    if (page == 1):
        prev = "#"
        next = "/?page=" + str(page + 1)
    elif (page == last):
        prev = "/?page=" + str(page - 1)
        next = "#"
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)

    return render_template('index.html', parameters=parameters, posts=posts, prev=prev, next=next)

@app.route("/about")
def about():
    return render_template('about.html', parameters=parameters)

# @app.route("/dashboard")
# def signin():
#     return render_template('sign.html', parameters=parameters)

@app.route ("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html',parameters=parameters, post=post)

@app.route("/uploader", methods = ['GET', 'POST'])
def uploader():
    if ('user' in session and session['user'] == parameters['admin_user']):
        if (request.method == 'POST'):
            f= request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename) ))
            return "Uploaded successfully"

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')

@app.route("/delete/<string:slno>", methods = ['GET', 'POST'])
def delete(slno):
    if ('user' in session and session['user'] == parameters['admin_user']):
        post = Posts.query.filter_by(slno=slno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():

    if ('user' in session and session['user'] == parameters['admin_user']):
        posts = Posts.query.all()
        return render_template('dashboard.html', parameters=parameters, posts = posts)


    if request.method=='POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if (username == parameters['admin_user'] and userpass == parameters['admin_password']):
            #set the session variable
            session['user'] = username
            posts = Posts.query.all()
            return render_template('dashboard.html', parameters=parameters, posts = posts)

    return render_template('login.html', parameters=parameters)

# @app.route("/post")
# def sample_post():
#     return render_template('post.html',parameters=parameters)
@app.route("/edit/<string:slno>", methods = ['GET', 'POST'])
def edit(slno):
    if ('user' in session and session['user'] == parameters['admin_user']):
        if request.method == 'POST':
            title = request.form.get('title')
            # tline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.now()

            if slno=='0':
                post = Posts(title=title, slug=slug, content=content, img_file=img_file, date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts.query.filter_by(slno=slno).first()
                post.title = title
                post.slug = slug
                post.content = content
                # post.tagline = tline
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect('/edit/'+slno)
        post = Posts.query.filter_by(slno=slno).first()
        return render_template('edit.html', parameters=parameters, post=post, slno=slno)

@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if (request.method=='POST'):
        name=request.form.get('name')
        email = request.form.get('email')
        phone_no = request.form.get('phone_no')
        message = request.form.get('message')
        entry=Contacts(name=name,  phone_no=phone_no,date=datetime.now(),message=message,email=email)
        db.session.add(entry);
        db.session.commit();
        recipients = [parameters['recipients']]
        mail.send_message('test message:-sending a mail using python flask mail library', sender=email, recipients=recipients, body="test messaging")

    '''
       sl.no,name,email,ph.no,message,date
       '''
    return render_template('contact.html', parameters=parameters)



# app.run(host="0.0.0.0", port=5000, debug=True)
app.run(port=5000,debug=True)