from flask import Blueprint, render_template
from __init__ import create_app

main = Blueprint('main', __name__)

@main.route('/') # home page that return 'index'
def index():
    return render_template('home.html')



app = create_app() # we initialize our flask app using the __init__.py function
if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True) # run the flask app on debug mode