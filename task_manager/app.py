from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from forms import TaskForm, RegistrationForm, LoginForm
from models import db, Task, User
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from datetime import datetime
import requests

app = Flask(__name__)

# Конфигурация приложения Flask
app.config['SECRET_KEY'] = 'asdfghjkl1234567890'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@host:port/database_name'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
db.init_app(app)

#создание таблиц базы данных 
with app.app_context():
    db.create_all()


def get_coordinates(city_name):
    """Получает географические координаты для заданного названия города."""
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': city_name,
        'format': 'json',
        'limit': 1
    }
    headers = {
        'User-Agent': 'Task Manager App (jaapanii01@gmail.com)' 
    }
    try:
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
        else:
            print(f"Не удалось найти координаты для города: {city_name}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API геокодирования: {e}")
        return None
    except Exception as e:
        print(f"Ошибка при обработке ответа API геокодирования: {e}")
        return None

def get_weather(latitude, longitude):
    """Получает текущую погоду по заданным географическим координатам с Open-Meteo."""
    base_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'current_weather': True,
        'temperature_unit': 'celsius',
        'windspeed_unit': 'kmh',
        'precipitation_unit': 'mm',
        'language': 'ru'
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        weather_data = response.json()
        return weather_data.get('current_weather') #чтобы избежать KeyError
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API погоды Open-Meteo: {e}")
        return None
    except Exception as e:
        print(f"Ошибка при обработке ответа API погоды Open-Meteo: {e}")
        return None
#хранения информации о погоде


@app.route('/new_task', methods=['GET', 'POST'])
def new_task():
    form = TaskForm()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        due_date = form.due_date.data
        location = form.location.data
        user_id = session.get('user_id')
        if user_id:
            new_task = Task(title=title, description=description, due_date=due_date, location=location, user_id=user_id)
            db.session.add(new_task)
            db.session.commit()
            flash('Задача успешно добавлена!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Вы не авторизованы для создания задач.', 'danger')
            return redirect(url_for('login'))
    return render_template('new_task.html', form=form)

"""# @app.route('/new_task', methods=['GET', 'POST'])
# def new_task():
#     ""Отображает форму для создания новой задачи и обрабатывает ее отправку.""
#     form = TaskForm() # Создаем экземпляр формы TaskForm
#     if form.validate_on_submit(): # Проверяем, была ли отправлена форма и все ли поля прошли валидацию
#         title = form.title.data
#         description = form.description.data
#         due_date = form.due_date.data
#         location = form.location.data
#         new_task = Task(title=title, description=description, due_date=due_date, location=location)
#         db.session.add(new_task) # Добавляем новую задачу в сессию базы данных
#         db.session.commit() # Фиксируем изменения в базе данных
#         flash('Задача успешно добавлена!', 'success') # Отображаем сообщение об успехе
#         return redirect(url_for('index')) # Перенаправляем пользователя на главную страницу
#     return render_template('new_task.html', form=form) # Отображаем форму для создания новой задачи
"""
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Отображает форму регистрации и обрабатывает регистрацию пользователя."""
    #cоздаем экземпляр RegistrationForm
    form = RegistrationForm() 
    # Проверяем, была ли отправлена форма
    if form.validate_on_submit(): 
        username = form.username.data
        password = form.password.data
        #проверяем существует ли пользователь с таким именем
        user = User.query.filter_by(username=username).first() 
        if user is None:
            #хэшируем пароль перед сохранением
            hashed_password = generate_password_hash(password) 
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Вы успешно зарегистрированы! Теперь вы можете войти.', 'success')
            return redirect(url_for('login')) #перенаправляем на входа
        else:
            flash('Имя пользователя уже занято.', 'warning')
    return render_template('register.html', form=form) #oтображаем регистрации

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Отображает форму входа и обрабатывает аутентификацию пользователя."""
    form = LoginForm() #создаем экземпляр
    if form.validate_on_submit(): #проверяем была ли отправлена форма
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first() #ищем пользователя
        if user and check_password_hash(user.password, password): #Проверяем совпадает ли пароль
            session['user_id'] = user.id #сохраняем ID пользователя в сессии
            flash('Вы успешно вошли!', 'success')
            return redirect(url_for('index')) #перенаправляем на главную
        else:
            flash('Неверное имя пользователя или пароль.', 'danger')
    return render_template('login.html', form=form) #отображаем форму входа

@app.route('/logout')
def logout():
    """Выходит из сессии пользователя."""
    session.pop('user_id', None) #удаляем ID пользователя
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index')) #перенаправляем на главную


@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    """Отображает форму для редактирования существующей задачи и обрабатывает ее отправку."""
    task = Task.query.get_or_404(task_id) #получаем задачу по ID или возвращаем 404
    form = TaskForm(obj=task) #инициализируем форму данными из объекта задачи
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due_date.data
        task.location = form.location.data
        db.session.commit()
        flash('Задача успешно обновлена!', 'success')
        return redirect(url_for('index'))
    return render_template('edit_task.html', form=form, task_id=task_id)


@app.route('/')
def index():
    print(session.get('user_id'))
    """Отображает список задач только для текущего пользователя с информацией о погоде."""
    user_id = session.get('user_id')
    tasks = []
    weather_info = {}
    if user_id:
        tasks = Task.query.filter_by(user_id=user_id).all()
        for task in tasks:
            if task.location and task.location not in weather_info:
                coordinates = get_coordinates(task.location)
                if coordinates:
                    latitude, longitude = coordinates
                    weather_data = get_weather(latitude, longitude)
                    weather_info[task.location] = weather_data
                else:
                    weather_info[task.location] = None
    return render_template('index.html', tasks=tasks, weather_info=weather_info)




@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    """Удаляет задачу из базы данных."""
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Задача успешно удалена!', 'info')
    return redirect(url_for('index')) 

if __name__ == '__main__':
    app.run(debug=True, port=5001)
