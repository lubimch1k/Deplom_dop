from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, BooleanField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Optional

class TaskForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired(), Length(max=80)])
    description = TextAreaField('Описание', validators=[Optional()])
    due_date = DateField('Срок выполнения', validators=[Optional()])
    location = StringField('Местоположение', validators=[Optional(), Length(max=100)])
    is_public = BooleanField('Сделать задачу публичной') # Новое поле
    submit = SubmitField('Сохранить задачу')

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=2, max=80)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')