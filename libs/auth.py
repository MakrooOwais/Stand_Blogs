import ast
import os
import boto3

from flask import Blueprint, render_template, redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from libs.models import User
from libs.db_blog import get_blogs_from_db, get_blog_from_db, add_comment, add_to_database, today
from libs.s3_cred import aws_access_key_id, aws_secret_access_key, aws_bucket_name
from libs.forms import LoginForm, RegisterForm, BlogForm, CommentForm
from libs.db_user import add_user


auth = Blueprint('auth', __name__) # create a Blueprint object that we name 'auth'



APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLD = "static/images/uploads"
UPLOAD_FOLDER = os.path.join(APP_ROOT, UPLOAD_FOLD)



boto3_client = boto3.client(
   "s3",
   aws_access_key_id = aws_access_key_id,
   aws_secret_access_key = aws_secret_access_key,
)

def save_boto3(image, path):
    bucket_name = aws_bucket_name
    boto3_client.upload_fileobj(
        image,
        bucket_name,
        path,
    )

@auth.route("/")
def home():
    blogs = get_blogs_from_db()
    return render_template("home.html", posts=blogs)


@auth.route("/post/<int:post_id>", methods=["GET", "POST"])  # /posts/0
@login_required
def posts(post_id):
    form = CommentForm()
    if form.validate_on_submit():
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
        image_dir = UPLOAD_FOLD + "/" + secure_filename(image.filename)
        save_boto3(image, image_dir)

        add_to_database(form.title.data, form.content.data, current_user.username, today,  "/" + image_dir, form.genre.data)

        return redirect(
            "/post/{}".format(
                len(get_blogs_from_db())+1 ),
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
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(request.args.get("next") or url_for("main.index"))
        error = "Invalid Username or Password"
    return render_template('sign_in.html', form=form, error = error)


@auth.route("/register", methods=['POST', 'GET'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        image = form.image.data
        image_dir =  UPLOAD_FOLD + "/user/" + form.username.data + os.path.splitext(secure_filename(image.filename))[1]
        save_boto3(image, path=image_dir)
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = add_user(username=form.username.data, password=hashed_password, picture= "/" + image_dir)       
        login_user(new_user, remember=True)
        return redirect(url_for('auth.home'))

    return render_template('register_user.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.home'))
