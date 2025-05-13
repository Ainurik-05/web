from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, SubmitField
from wtforms.validators import DataRequired, Length
import os

# Инициализация приложения
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///musicapp.db'
app.config['UPLOAD_FOLDER'] = 'static/music'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация базы данных
db = SQLAlchemy(app)

# Настройка Login Manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# Формы
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


# Модели базы данных
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    playlists = db.relationship('Playlist', backref='owner', lazy=True)


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    songs = db.Column(db.String(500), nullable=True)


# Загрузчик пользователей для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Маршруты
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('playlists'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('playlists'))
        flash('Неверный логин или пароль!')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Регистрация успешна! Теперь вы можете войти.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        if 'music_file' not in request.files or form.music_file.data.filename == '':
            flash('Выберите файл для загрузки!')
            return redirect(request.url)

        file = form.music_file.data
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Создаем плейлист с загруженной песней
        playlist = Playlist(name=filename, user_id=current_user.id, songs=filename)
        db.session.add(playlist)
        db.session.commit()

        flash('Файл загружен успешно!')
        return redirect(url_for('playlists'))
    return render_template('upload.html', form=form)


@app.route('/playlists', methods=['GET'])
@login_required
def playlists():
    playlists = Playlist.query.filter_by(user_id=current_user.id).all()
    return render_template('playlist.html', playlists=playlists)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# Создание базы данных
def init_db():
    with app.app_context():
        db.create_all()


# Точка входа
if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)