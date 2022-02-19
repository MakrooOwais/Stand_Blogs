import ast
import os

from minio import Minio
from flask import Blueprint, render_template, redirect, url_for, request, g
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from libs.models import User
from libs.db_blog import get_blogs_from_db, get_blog_from_db, add_comment, add_to_database, today
from libs.s3_cred import aws_access_key_id, aws_secret_access_key, aws_bucket_name, aws_region
from libs.forms import LoginForm, RegisterForm, BlogForm, CommentForm
from libs.db_user import add_user


auth = Blueprint('auth', __name__) # create a Blueprint object that we name 'auth'



APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLD = "static/images/uploads"
UPLOAD_FOLDER = os.path.join(APP_ROOT, UPLOAD_FOLD)

IMAGE_FOLDER = "http://192.168.1.5:9000/"+ aws_bucket_name + "/static/images/uploads/"

s3_client = Minio(
    "192.168.1.5:9000",
    access_key = aws_access_key_id,
    secret_key = aws_secret_access_key,
    region = aws_region,
    secure=False
)

def save_s3(image, path):
    s3_client.fput_object(aws_bucket_name, 'static/images/uploads/{}'.format(path), path, content_type='image/jpeg')

@auth.route("/")
def home():
    blogs = get_blogs_from_db()
    return render_template("home.html", posts=blogs)


@auth.route("/post/<int:post_id>", methods=["GET", "POST"])
@login_required
def posts(post_id):
    form = CommentForm()
    if form.submit.data:
        message = form.comment.data
        add_comment(post_id, message)
        return redirect(
            "/post/{}".format(
                post_id
            )
        )
        

    post = get_blog_from_db(post_id=post_id)
    if not post:
        return render_template(
            "404.jinja2", message=f"A post with ID {post_id} was not found."
        )

    if post["comments"]:
        no_of_comments = len(ast.literal_eval(post["comments"]))
        comments = ast.literal_eval(post["comments"])
    else:
        no_of_comments = 0
        comments = {}

    blogs = get_blogs_from_db()
    return render_template(
        "post.html", post=post, posts=blogs, no=no_of_comments, comments=comments, form= form
    )


@auth.route("/post/create", methods=["GET", "POST"])
@login_required
def create():
    form = BlogForm()
    if form.submit.data:
        image = form.file.data
        image.save(secure_filename(image.filename))
        image_dir = secure_filename(image.filename)
        save_s3(image, image_dir)
        os.remove(image_dir)

        add_to_database(form.title.data, form.content.data, current_user.user_name, today,  image_dir, form.genre.data)

        return redirect(
            "/post/{}".format(
                len(get_blogs_from_db())),
            )

    return render_template("new_blog.html", form=form)


@auth.route("/all_blogs_posts")
def all_blog_posts():
    blogs = get_blogs_from_db()
    return render_template("blog_entries.html", posts=blogs)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None
    if form.submit.data:
        user = User.query.filter_by(user_name=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(request.args.get("next") or url_for("main.index"))
        error = "Invalid Username or Password"
    return render_template('sign_in.html', form=form, error = error)


@auth.route("/register", methods=['POST', 'GET'])
def register():
    form = RegisterForm()

    if form.submit.data:
        image = form.image.data
        image_dir =  form.username.data + os.path.splitext(secure_filename(image.filename))[1]
        image.save(image_dir)
        save_s3(image, path=image_dir)
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = add_user(username=form.username.data, password=hashed_password, picture= image_dir)
        os.remove(image_dir)
        login_user(new_user, remember=True)
        return redirect(url_for('auth.home'))

    return render_template('register_user.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.home'))
