from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_minio import Minio
from flask_cdn import CDN


from libs.s3_cred import aws_access_key_id, aws_secret_access_key, aws_bucket_name, aws_region
from libs.db_cred import db_username, db_password, db_host, db_name

db = SQLAlchemy()
s3 = Minio()
cdn = CDN()

def create_app():
    app = Flask(__name__, static_url_path=None)
    from libs.auth import auth as auth_blueprint, UPLOAD_FOLDER
    from main import main as main_blueprint
    app.config['SECRET_KEY'] = "secret"
    app.config['FLASKS3_BUCKET_NAME'] = aws_bucket_name
    app.config['MINIO_URL'] = '192.168.1.5:9000'
    app.config['MINIO_ROOT_USER'] = aws_access_key_id
    app.config['MINIO_ROOT_PASSWORD'] = aws_secret_access_key
    app.config['MINIO_REGION'] = aws_region
    app.config['MINIO_SECURE'] = False
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqldb://{db_username}:{db_password}@{db_host}/{db_name}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    s3.init_app(app)
    login_manager = LoginManager() 
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
   
    from libs.models import User
    @login_manager.user_loader
    def load_user(user_Id):
        return User.query.get(int(user_Id))
        
    @app.context_processor
    def get_current_user():
        return {"current_user": current_user}
    
    @app.context_processor
    def set_url():
        return {"url": "http://192.168.1.5:9000/"+ aws_bucket_name + "/static/" }     
    app.register_blueprint(auth_blueprint)
    
    app.register_blueprint(main_blueprint)
    return app