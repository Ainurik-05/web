from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=150)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6, max=150)])
    submit = SubmitField('Войти')

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=150)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6, max=150)])
    submit = SubmitField('Зарегистрироваться')

class UploadForm(FlaskForm):
    music_file = FileField('Выберите музыкальный файл', validators=[DataRequired()])
    submit = SubmitField('Загрузить')