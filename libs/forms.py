from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField
from wtforms.fields import TextAreaField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import InputRequired, Length, DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Submit')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    image = FileField('Image', validators=[FileRequired()])
    submit = SubmitField('Submit')

class CommentForm(FlaskForm):
    comment = TextAreaField('Comment', validators=[InputRequired(), Length(min=4, max=100)])
    submit = SubmitField('Submit')

class BlogForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired(), Length(min=4, max=15)])
    content = TextAreaField('Content', validators=[InputRequired(), Length(min=4, max=1000)])
    file = FileField('Image', validators=[FileRequired()])
    genre = SelectField(
        'Title',
        [DataRequired()],
        choices=[
            ('Farmer', 'farmer'),
            ('Corrupt Politician', 'politician'),
            ('No-nonsense City Cop', 'cop'),
            ('Professional Rocket League Player', 'rocket'),
            ('Lonely Guy At A Diner', 'lonely'),
            ('Pokemon Trainer', 'pokemon')
        ]
    )
    submit = SubmitField('Submit')
