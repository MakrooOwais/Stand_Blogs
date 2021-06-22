import os
import ast
import mysql.connector
import re

from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, url_for, redirect
from datetime import date
#from flask_fontawesome import FontAwesome

session = {"username": None, "logged_in": False, "Id": None}
# Enter your database connection details below


d2 = date.today()
today = d2.strftime("%B, %d, %Y")


# Init App
app = Flask(__name__, instance_relative_config=True)

app.secret_key = "your secret key"

#fa = FontAwesome(app)


config = {
    'user': 'sql6420751',
    'password': 'MGRiWsnmSA',
    'host': 'sql6.freemysqlhosting.net',
    'database': 'sql6420751',
}

#pAqx@LvV2vX2Dvu
# now we establish our connection

connection = mysql.connector.connect(**config)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLD = "static/images/uploads"
UPLOAD_FOLDER = os.path.join(APP_ROOT, UPLOAD_FOLD)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER



def add_to_database(title, content, author, date, image, genre):
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO blogs (title, content, author, date_, image, genre) VALUES (%s, %s, %s, %s, %s, %s)",
        (title, content, author, date, image, genre),
    )
    connection.commit()
    return None


def add_comment(post_id: int, comment):
    cursor = connection.cursor()
    cursor.execute("SELECT comments FROM blogs where Id = %s", (post_id,))
    comment_old = cursor.fetchone()[0]
    if comment_old:
        comment_new = comment_old + comment
    else:
        comment_new = comment
    print(comment_new)
    cursor.execute(
        "UPDATE blogs SET comments = %s WHERE Id = %s",
        (
            comment_new,
            post_id,
        ),
    )
    connection.commit()
    return None


def get_blog_from_db(post_id):
    blog_post = {}
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM blogs WHERE Id = {}".format(post_id,))
    for row in cursor:
        blog_post = {
            "Id": row[0],
            "title": row[1],
            "content": row[2],
            "author": row[3],
            "date": row[4],
            "image": row[5],
            "genre": row[6],
            "comments": row[7],
        }
    return blog_post


def get_blogs_from_db():
    blogs = []
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM blogs ORDER BY Id DESC")
    for row in cursor:
        blogs.append(
            {
                "Id": row[0],
                "title": row[1],
                "content": row[2],
                "author": row[3],
                "date": row[4],
                "image": row[5],
                "genre": row[6],
                "comments": row[7],
            }
        )
    return blogs


@app.route("/")
def home():
    blogs = get_blogs_from_db()
    return render_template("home.html", posts=blogs)


@app.route("/post/<int:post_id>", methods=["GET", "POST"])  # /posts/0
def posts(post_id):
    if request.method == "POST":
        message = request.form["message"]
        comment = (
            "{ 'user_name' : "
            + "'abc', "
            + "'message' : '"
            + message
            + "', 'date' : '"
            + today
            + "' }, "
        )
        add_comment(post_id, comment)
        return redirect(
            "/post/{}".format(
                post_id,
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
        print(comments)
    else:
        no_of_comments = 0
        comments = {}

    blogs = get_blogs_from_db()
    return render_template(
        "post.html", post=post, posts=blogs, no=no_of_comments, comments=comments
    )


@app.route("/post/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        author = request.form.get("author")
        genre = request.form.get("genre")
        img = request.files["image"]
        image = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(img.filename))
        image_dir = "/" + UPLOAD_FOLD + "/" + secure_filename(img.filename)
        img.save(image)


        add_to_database(title, content, author, today, image_dir, genre)

        return redirect(
            "/post/{}".format(
                len(get_blogs_from_db())),
            )

    return render_template("new_blog.html")


@app.route("/all_blogs_posts")
def all_blog_posts():
    blogs = get_blogs_from_db()

    return render_template("blog_entries.html", posts=blogs)


@app.route("/pythonlogin/register", methods=["GET", "POST"])
def register():
    # Output message if something goes wrong...
    msg = ""
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
        and "email" in request.form
    ):
        # Create variables for easy access
        username = request.form["username"]
        password = request.form["password"]
        img = request.files["image"]
        image = os.path.join(app.root_path, app.config["UPLOAD_FOLDER"], secure_filename(img.filename))
        image_dir = "/" + UPLOAD_FOLD + "/" + secure_filename(img.filename)
        img.save(image)

        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                account = cursor.fetchone()
                # If account exists show error and validation checks
                if account:
                    msg = "Account already exists!"
                elif not re.match(r"[A-Za-z0-9]+", username):
                    msg = "Username must contain only characters and numbers!"
                else:
                    # Account doesnt exists and the form data is valid, now insert new account into users table
                    cursor.execute(
                        "INSERT INTO users VALUES (NULL, %s, %s, %s)",
                        (
                            username,
                            password,
                            image_dir,
                        ),
                    )
                    mysql.connection.commit()
                    msg = "You have successfully registered!"
    elif request.method == "POST":
                    # Form is empty... (no POST data)
                    msg = "Please fill out the form!"
                # Show registration form with message (if any)
    return render_template("register_user.html", msg=msg)


@app.route("/pythonlogin/", methods=["GET", "POST"])
def login():
    msg = ""
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
    ):
        username = request.form["username"]
        password = request.form["password"]
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM users WHERE username = %s AND password = %s",
                    (
                        username,
                        password,
                    ),
                )
                account = cursor.fetchone()
                if account:
                    session["logged_in"] = True
                    session["id"] = account["id"]
                    session["username"] = account["username"]
                    return "Logged in successfully!"
                else:
                    msg = "Incorrect username/password!"
    return render_template("index.html", msg=msg)


@app.route("/pythonlogin/logout")
def logout():
    session.pop("logged_in", False)
    session.pop("id", None)
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route("/pythonlogin/profile")
def profile():
    # Check if user is loggedin
    if "logged_in" in session:
        # We need all the account info for the user so we can display it on the profile page
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %s", (session["id"],))
                account = cursor.fetchone()
                # Show the profile page with account info
        return render_template("profile.html", account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=False, host='127.0.0.1', port=8080)