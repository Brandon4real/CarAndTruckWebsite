from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import LoginForm, RegisterForm, UploadCarForm, CommentForm
from flask_gravatar import Gravatar
import os
from werkzeug.utils import secure_filename
import uuid as uuid
import glob
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'some-password'
uuid_key = str(uuid.uuid4())
UPLOAD_FOLDER = "static/uploads/{}".format(uuid_key)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ckeditor = CKEditor(app)
Bootstrap(app)
gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False,
                    base_url=None)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


##CONFIGURE TABLE
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    type_of_car = db.Column(db.Text, nullable=False)
    price_of_car = db.Column(db.Integer, nullable=False)
    car_description = db.Column(db.Text, nullable=False)
    propulsion = db.Column(db.Text, nullable=False)
    make_of_car = db.Column(db.Integer, nullable=False)
    gearbox = db.Column(db.Text, nullable=False)
    kilometers = db.Column(db.Integer, nullable=True)
    tel_number = db.Column(db.Integer, nullable=False)
    full_option = db.Column(db.Text, nullable=False)
    images = db.Column(db.String(), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    comments = relationship("Comment", back_populates="parent_post")
    uuid_key = db.Column(db.String(), nullable=False)


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    parent_post = relationship("BlogPost", back_populates="comments")
    comment_author = relationship("User", back_populates="comments")
    text = db.Column(db.Text, nullable=False)


db.create_all()


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1 or current_user.is_anonymous or not current_user.is_authenticated:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
# changed get_all_posts to home
def home():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts, current_user=current_user, )


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        if User.query.filter_by(email=form.email.data).first():
            print(User.query.filter_by(email=form.email.data).first())
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home"))

    return render_template("register.html", form=form, current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/about")
def about():
    return render_template("about-us.html", current_user=current_user)


@app.route("/contact")
def contact():
    return render_template("contact.html", current_user=current_user)


# changed new-post to /uploads
@app.route("/uploads", methods=["GET", "POST"])
@admin_only
def add_new_post():
    global destination
    form = UploadCarForm()

    if form.validate_on_submit():
        try:
            os.mkdir(app.config['UPLOAD_FOLDER'])
        except FileExistsError:
            pass
        files_filenames = []
        for file in form.files.data:
            file_filename = secure_filename(file.filename)
            image_name = str(uuid.uuid4()) + "_" + file_filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_name))
            files_filenames.append(image_name)
            destination = '/'.join([app.config['UPLOAD_FOLDER'], image_name])
        #  print(files_filenames)

        new_post = BlogPost(
            type_of_car=form.type_of_car.data,
            price_of_car=form.price_of_car.data,
            car_description=form.car_description.data,
            propulsion=form.propulsion.data,
            make_of_car=form.make_of_car.data,
            gearbox=form.gear_box.data,
            kilometers=form.kilometers.data,
            tel_number=form.tel_number.data,
            full_option=form.full_option.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y"),
            images=destination,
            uuid_key=uuid_key

        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("home"))

    return render_template("upload.html", form=form, current_user=current_user, uuid_key=uuid)


@app.route("/post/<int:post_id>/<uuid_key>", methods=["GET", "POST"])
def show_post(post_id, uuid_key):
    form = CommentForm()
    requested_post = BlogPost.query.get(post_id)
    uuid = BlogPost.query.get(uuid_key)

    files = []
    for uuid in glob.glob("{}/*.*".format(app.config['UPLOAD_FOLDER'])):
        if not os.path.isdir(app.config['UPLOAD_FOLDER']):
            return "Error! {} not found!".format(app.config['UPLOAD_FOLDER'])
        else:
            for file in app.config['UPLOAD_FOLDER']:
                fname = file
                files.append(fname)
            print(files)

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        new_comment = Comment(
            text=form.comment_text.data,
            comment_author=current_user,
            parent_post=requested_post
        )
        db.session.add(new_comment)
        db.session.commit()

    return render_template("car_details.html", post=requested_post,
                           form=form, current_user=current_user, post_id=post_id, uuid_key=uuid, files=files)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = UploadCarForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=current_user,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form, is_edit=True, current_user=current_user)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


# added statements
@app.route('/trucks', methods=['GET', 'POST'])
def trucks():
    return render_template("trucks.html", )


@app.route('/blog')
def blog():
    return render_template("blog.html", current_user=current_user)


@app.route('/team')
def team():
    return render_template("team.html", current_user=current_user)


@app.route('/testimonials')
def testimonials():
    return render_template("testimonials.html", current_user=current_user)


@app.route('/terms')
def terms():
    return render_template("terms.html", current_user=current_user)


# @app.route('/car_details', methods=["GET", "POST"])
# def car_details():
# return render_template("car_details.html", current_user=current_user, )


@app.route('/blog_details')
def blog_details():
    return render_template("blog_details.html", current_user=current_user)


if __name__ == "__main__":
    app.run(debug=True)
