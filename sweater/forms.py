from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, BooleanField, SelectField, FileField
from wtforms.validators import DataRequired, InputRequired, Email, EqualTo, regexp


class AddUserForm(FlaskForm):
    first_name = StringField('Имя пользователя', [DataRequired(message='Форма не может быть пустой')])
    last_name = StringField('Фамилия пользователя', [DataRequired(message='Форма не может быть пустой')])
    patronymic = StringField('Отчество пользователя', [DataRequired(message='Форма не может быть пустой')])
    email = StringField('Почта пользователя',
                        [DataRequired(message='Форма не может быть пустой'), Email(message="некорректный email")])
    password = PasswordField('Пароль ', [DataRequired(message='Форма не может быть пустой'),
                                         EqualTo('confirm', message='Пароли должны сопавдатЬ!')])
    confirm = PasswordField('Повторите пароль', [DataRequired(message='Форма не может быть пустой')])
    photo = FileField('Фотография')
    role = BooleanField('Админ')
    submit = SubmitField('Добавить пользователя')


class LoginForm(FlaskForm):
    email = StringField('Почта пользователя',
                        [DataRequired(message='Форма не может быть пустой'), Email(message="некорректный email")])
    password = PasswordField('Пароль ', [DataRequired(message='Форма не может быть пустой')])
    submit = SubmitField('Войти')


class UserForm(FlaskForm):
    first_name = StringField('Имя пользователя', [DataRequired(message='Форма не может быть пустой')], render_kw={'readonly': True})
    last_name = StringField('Фамилия пользователя', [DataRequired(message='Форма не может быть пустой')], render_kw={'readonly': True})
    patronymic = StringField('Отчество пользователя', [DataRequired(message='Форма не может быть пустой')], render_kw={'readonly': True})
    email = StringField('Почта пользователя',
                        [DataRequired(message='Форма не может быть пустой'), Email(message="некорректный email")])
    password = PasswordField('Пароль ', [DataRequired(message='Форма не может быть пустой'),
                                         EqualTo('confirm', message='Пароли должны сопавдатЬ!')])
    confirm = PasswordField('Повторите пароль', [DataRequired(message='Форма не может быть пустой')])
    photo = FileField('Фотография')
    role = BooleanField('Админ', render_kw={'readonly': True})
    submit = SubmitField('Добавить пользователя')


class AddBuildingForm(FlaskForm):
    address = StringField('Адрес', [DataRequired(message='Форма не может быть пустой')])
    photo = FileField('Фотография')
    submit = SubmitField('Добавить корпус')


class AddCategoryForm(FlaskForm):
    name = StringField('Название категории', [DataRequired(message='Форма не может быть пустой')])
    submit = SubmitField('Добавить корпус')