from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from PIL import Image
from flask import send_from_directory
import pickle
app = Flask(__name__)
lastpage=''
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = r'static\img'
app.secret_key = 'Ket'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
db = SQLAlchemy(app)
class PageRemember():


    def __init__(self):
        lastpage='/'
        search=''
        avatar=''


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable = False, unique=True)
    user = db.Column(db.String(31), nullable=False)
    comment_text = db.Column(db.Text)
    article = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Comments%r>' % self.id


class Articles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    intro = db.Column(db.String(150), nullable=False)
    full_text = db.Column(db.Text)
    author = db.Column(db.String(31), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Articles%r>' % self.id


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable = False, unique=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(16), nullable=False)
    email = db.Column(db.String(), nullable=False, unique=True)
    date=db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Users%r>' % self.id


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        return redirect(f'/search-posts/{request.form["Search"]}')
    remember.lastpage='/'
    return render_template('index.html', user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(remember.lastpage)


@app.route('/create_article', methods=['POST', 'GET'])
def create_article():
    remember.lastpage='/create_article'
    if request.method == 'POST':
        try:
            return redirect(f'/search-posts/{request.form["Search"]}')
        except:
            if not request.form['title'] or not request.form['intro'] or not request.form['full_text']:
                flash("All the fields shouldn't be empty")
                return redirect('/create_article')
            else:
                try:
                    title = request.form['title']
                    intro = request.form['intro']
                    full_text = request.form['full_text']
                    author = request.form['username']

                    article = Articles(title=title, intro=intro, full_text=full_text, author=author)
                    try:
                        db.session.add(article)
                        db.session.commit()
                        return redirect('/posts')
                    except:
                        return "An error happened(( Please try again"
                except:
                    return redirect(f'/search-posts/{request.form["Search"]}')
    else:
        return render_template('create.html', user=current_user)


@app.route('/register', methods=['POST', 'GET'])
def create_account():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            user = Users(username=username, password=password, email=email)
            try:
                db.session.add(user)
                db.session.commit()
            except:
                return "An error happened(( Please try again"
            user = Users.query.filter_by(username=username).first()
            os.mkdir(f"D:/paiton/flask site/static/img/{user.username}")
            basedir = os.path.abspath(os.path.dirname(__file__))
            img = Image.open('noavatar.png')
            img = img.save(os.path.join(basedir, app.config["UPLOAD_FOLDER"],username,'ava.png'))
            return redirect(remember.lastpage)
        except:
            return redirect(f'/search-posts/{request.form["Search"]}')

    else:
        return render_template('create_user.html', user=current_user)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


@app.route('/userpage', methods=['POST', 'GET'])
def userpage():
    remember.lastpage = '/userpage'
    if request.method == 'POST':
        return redirect(f'/search-posts/{request.form["Search"]}')

    else:
        if current_user:
            basedir = os.path.abspath(os.path.dirname(__file__))
            ava= os.listdir(os.path.join(basedir, app.config['UPLOAD_FOLDER'], current_user.username))[0]
            return render_template('userpage.html', user=current_user, ava=ava)
        else:
            return redirect('/')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        try:
            password = request.form['password']
            user = Users.query.filter_by(username=request.form['username'], password=password).first()
            if not user:
                flash(u'<script language="JavaScript">alert("Please check your login details and try again.")</script>', 'error' )
                return redirect('/login')
            else:
                login_user(user)
                return redirect(remember.lastpage)
        except:
            return redirect(f'/search-posts/{request.form["Search"]}')

    else:
        return render_template('login.html', user=current_user)


@app.route('/posts/<int:id>/edit', methods=['POST', 'GET'])
def edit_article(id):
    remember.lastpage = f'/posts/{id}/edit'
    article = Articles.query.get_or_404(id)
    if request.method == 'POST':
        article.title = request.form['title']
        article.intro = request.form['intro']
        article.full_text = request.form['full_text']
        try:
            db.session.commit()
            return redirect('/posts/<int:id>')
        except:
            return "An error happened(( Please try again"
    else:
        return render_template('edit_article.html', article=article, user=current_user)


@app.route('/about')
def about():
    remember.lastpage=f'/about'
    return render_template('about.html', user=current_user)


@app.route('/posts', methods=['GET', 'POST'])
def posts():
    if request.method == 'POST':
        return redirect(f'/search-posts/{request.form["Search"]}')
    else:
        myposts = Articles.query.order_by(Articles.date.desc()).all()
        return render_template('posts.html', articles=myposts, user=current_user)


@app.route('/posts/<int:id>', methods=['POST', 'GET'])
def post_details(id):
    remember.lastpage = f'/posts/{id}'
    if request.method == 'POST':
        try:
            full_text=request.form['full_text']
            author = request.form['user']
            article = id
            comment = Comments(comment_text=full_text, user=author, article=article)
            try:
                db.session.add(comment)
                db.session.commit()
                return redirect(remember.lastpage)
            except:
                return redirect('/posts')
        except:
            return redirect(f'/search-posts/{request.form["Search"]}')
    else:
        mypost = Articles.query.get(id)
        comments = Comments.query.order_by(Comments.date.desc()).filter_by(article = mypost.id).all()
        basedir = os.path.abspath(os.path.dirname(__file__))
        ava_dict = dict()
        for c in comments:

            ava_dict[c.user]= os.listdir(os.path.join(basedir,app.config['UPLOAD_FOLDER'],c.user))[0]
            print(ava_dict)


        return render_template('post_detail.html', article=mypost, user=current_user, comments=comments, avas=ava_dict)


@app.route('/posts/<int:id>/delete')
def post_delete(id):
    mypost = Articles.query.get_or_404(id)
    try:
        db.session.delete(mypost)
        db.session.commit()
        return redirect('/posts')
    except:
        return "An error happened while deleting this article. Please try again later"


@app.route('/search-posts/<string:pages>', methods=['POST', 'GET'])
def search_results(pages):
    if request.method == 'POST':
        return redirect(f'/search-posts/{request.form["Search"]}')
    else:
        mypost = Articles.query.order_by(Articles.id).all()
        return render_template('search_results.html', pages=pages, user=current_user, article=mypost)


@app.route('/edit/<string:name>', methods=['POST', 'GET'])
def edit_user(name):
    mypost = Articles.query.get_or_404(current_user.id)
    if request.method == 'POST':
        current_user.username = request.form['username']
        current_user.password = request.form['password']
        file = request.files['file']
        print(file)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            basedir = os.path.abspath(os.path.dirname(__file__))
            try:
                file.save(os.path.join(basedir,app.config['UPLOAD_FOLDER'],str(current_user.username), filename))
                os.rename(os.path.join(basedir,app.config['UPLOAD_FOLDER'],str(current_user.username), filename),
                      os.path.join(basedir,app.config['UPLOAD_FOLDER'],str(current_user.username), f'ava.{filename.split(".")[1]}'))
            except(FileExistsError):
                os.remove(os.path.join(basedir,app.config['UPLOAD_FOLDER'],str(current_user.username), f'ava.{filename.split(".")[1]}'))
                # file.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], str(current_user.username), filename))
                os.rename(os.path.join(basedir, app.config['UPLOAD_FOLDER'], str(current_user.username), filename),
                          os.path.join(basedir, app.config['UPLOAD_FOLDER'], str(current_user.username),
                                       f'ava.{filename.split(".")[1]}'))
            return redirect('/userpage')
        return redirect('/userpage')
    else:
        return render_template('edit_user.html', user=current_user, articles=mypost)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/user/<string:name>',methods=['POST', 'GET'])
def show_user(name):
    userok=Users.query.filter_by(username=name).first()
    basedir = os.path.abspath(os.path.dirname(__file__))
    ava = os.listdir(os.path.join(basedir, app.config['UPLOAD_FOLDER'], userok.username))[0]
    if request.method == 'POST':
        return redirect(f'/search-posts/{request.form["Search"]}')
    return render_template('user.html', user=current_user, user1=userok, ava=ava)




if __name__ == '__main__':
    remember = PageRemember()
    app.run(debug=True)