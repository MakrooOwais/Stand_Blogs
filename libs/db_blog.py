
from datetime import date

from libs.models import Blogs
from flask_login import current_user
from __init__ import db


d2 = date.today()
today = d2.strftime("%B, %d, %Y")

def add_to_database(title_, content_, author_, date, image_, genre_):
    new_blog = Blogs(title = title_, content = content_, author = author_, date_ = date, image = image_, genre = genre_)
    db.session.add(new_blog)
    db.session.commit()
    return None


def add_comment(post_id: int, message):
    comment = (
            "{ 'username' : "
            + "'{}', ".format(current_user.user_name)
            + "'picture': '{}',".format(current_user.picture)
            + "'message' : '"
            + message
            + "', 'date' : '"
            + today
            + "' }, "
        )
    comment_old = None
    blog = Blogs.query.filter_by(Id=post_id).first()
    print(blog)
    comment_old = blog.comments
    if comment_old:
        comment_new = comment_old + comment
    else:
        comment_new = comment
    blog.comments = comment_new
    db.session.commit()
    return None


def get_blog_from_db(post_id):
    blog_post = {}
    row = Blogs.query.filter_by(Id=post_id).first()
    blog_post = {
        "Id": row.Id,
        "title": row.title,
        "content": row.content,
        "author": row.author,
        "date": row.date_,
        "image": row.image,
        "genre": row.genre,
        "comments": row.comments,
    }
    return blog_post


def get_blogs_from_db():
    blogs = []
    rows = db.session.query(Blogs).all()
    for row in rows:
        blogs.append({
            "Id": row.Id,
            "title": row.title,
            "content": row.content,
            "author": row.author,
            "date": row.date_,
            "image": row.image,
            "genre": row.genre,
            "comments": row.comments,
        })
    
    return sorted(blogs, key = lambda i: i['Id'],reverse=True)

