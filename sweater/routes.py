from flask import render_template, request, redirect, flash, url_for, send_file
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from os import path, remove

from sweater import app, db
from models import User, Building,Category
from forms import AddUserForm, LoginForm, UserForm, AddBuildingForm, AddCategoryForm


@app.route('/', methods=['POST', 'GET'])
@login_required
def index():
    return render_template('index.html')


@app.route('/create_user', methods=['POST', 'GET'])
@login_required
def create_user():
    access = db.session.get(User, current_user.get_id())
    if access.role:
        form = AddUserForm()
        if form.validate_on_submit():
            # Запрашиваем в база пользователя по email
            is_user = User.query.filter_by(email=form.email.data).first()
            if is_user:
                # Если email занят, сообщаем об этом пользователю
                flash('Пользователь с таким email уже зарегистрирован!')
                return redirect(url_for('add_user'))
            user = User(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                patronymic=form.patronymic.data,
                email=form.email.data,
                role=form.role.data,
                password=generate_password_hash(form.password.data)
            )
            db.session.add(user)
            db.session.commit()
            filename = f'avatars/{user.id}.{secure_filename(form.photo.data.filename)}'
            file_path = path.join(app.config['UPLOAD_FOLDER'], filename)
            form.photo.data.save(file_path)
            user.photo = file_path
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login_page'))
        return render_template('create_user.html', form=form, notification=True)
    else:
        return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('index'))
        else:
            flash('Логин или пароль не корректны!')
    else:
        flash('Пожалуйста, заполните пропущенные ячейки!')
    return render_template('login.html', form=form)


@app.route('/users', methods=['POST', 'GET'])
@login_required
def users():
    access = db.session.get(User, current_user.get_id())
    if access.role:
        data = User.query.order_by(User.id).all()
        return render_template('users.html', data=data)
    else:
        return redirect(url_for('index'))


@app.route('/profile/<int:user_id>', methods=['POST', 'GET'])
@login_required
def profile(user_id):
    access = db.session.get(User, current_user.get_id())
    if access.role:
        user = db.session.get(User, user_id)
        form = UserForm(first_name=user.first_name,
                        last_name=user.last_name,
                        patronymic=user.patronymic,
                        email=user.email,
                        role=user.role)
        if form.validate_on_submit():
            # Запрашиваем в база пользователя по email
            is_user = User.query.filter_by(email=form.email.data).first()
            if is_user:
                if is_user.email != user.email:
                    # Если email занят, сообщаем об этом пользователю
                    flash('Пользователь с таким email уже зарегистрирован!')
                    return redirect(url_for('add_user'))
            user.email = form.email.data
            user.password = generate_password_hash(form.password.data)

            if form.photo.data:
                remove(path.join(app.root_path, user.photo))
                filename = f'avatars/{user.id}.{secure_filename(form.photo.data.filename)}'
                file_path = path.join(app.config['UPLOAD_FOLDER'], filename)
                form.photo.data.save(file_path)
                user.photo = file_path
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('profile', user_id=user_id))

        return render_template('create_user.html', form=form, notification=True, photo=access.photo)
    else:
        return redirect(url_for('index'))


@app.route('/upload/<path:file>', methods=['GET', 'POST'])
@login_required
def upload(file):
    uploads = path.join(app.root_path, file)
    return send_file(uploads, file)


@app.route('/edit_user/<int:user_id>', methods=['POST', 'GET'])
@login_required
def edit_user(user_id):
    access = db.session.get(User, current_user.get_id())
    if access.role:
        user = db.session.get(User, user_id)
        form = AddUserForm(first_name=user.first_name,
                           last_name=user.last_name,
                           patronymic=user.patronymic,
                           email=user.email,
                           role=user.role)
        if form.validate_on_submit():
            # Запрашиваем в база пользователя по email
            is_user = User.query.filter_by(email=form.email.data).first()
            if is_user:
                if is_user.email != user.email:
                    # Если email занят, сообщаем об этом пользователю
                    flash('Пользователь с таким email уже зарегистрирован!')
                    return redirect(url_for('add_user'))
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.patronymic = form.patronymic.data
            user.email = form.email.data
            user.role = form.role.data
            user.password = generate_password_hash(form.password.data)

            if form.photo.data:
                remove(path.join(app.root_path, user.photo))
                filename = f'avatars/{user.id}.{secure_filename(form.photo.data.filename)}'
                file_path = path.join(app.config['UPLOAD_FOLDER'], filename)
                form.photo.data.save(file_path)
                user.photo = file_path
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('users'))

        return render_template('create_user.html', form=form, notification=True)
    else:
        return redirect(url_for('index'))


@app.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    access = db.session.get(User, current_user.get_id())
    if access.role or access.id == access.id:
        remove(path.join(app.root_path, db.session.get(User, user_id).photo))
        delete = db.session.get(User, user_id)
        db.session.delete(delete)
        db.session.commit()
        return redirect(url_for('users'))


@app.route('/buildings', methods=['POST', 'GET'])
@login_required
def buildings():
    data = Building.query.order_by(Building.id).all()
    return render_template('buildings.html', data=data)


@app.route('/create_building', methods=['POST', 'GET'])
@login_required
def create_building():
    access = db.session.get(User, current_user.get_id())
    if access.role:
        form = AddBuildingForm()
        if form.validate_on_submit():
            # Запрашиваем в база пользователя по email
            is_address = Building.query.filter_by(address=form.address.data).first()
            if is_address:
                # Если email занят, сообщаем об этом пользователю
                flash('Корпус по данному адресу уже зарегистрирован!')
                return redirect(url_for('create_building'))
            building = Building(
                address=form.address.data
            )
            db.session.add(building)
            db.session.commit()
            filename = f'building/{building.id}.{secure_filename(form.photo.data.filename)}'
            file_path = path.join(app.config['UPLOAD_FOLDER'], filename)
            form.photo.data.save(file_path)
            building.photo = file_path
            db.session.add(building)
            db.session.commit()
            return redirect(url_for('buildings'))
        return render_template('create_building.html', form=form, notification=True)
    else:
        return redirect(url_for('index'))


@app.route('/edit_building/<int:building_id>', methods=['POST', 'GET'])
@login_required
def edit_building(building_id):
    access = db.session.get(User, current_user.get_id())
    if access.role:
        building = db.session.get(Building, building_id)
        form = AddBuildingForm(address=building.address)
        if form.validate_on_submit():
            # Запрашиваем в база пользователя по email
            is_building = Building.query.filter_by(address=form.address.data).first()
            if is_building:
                if is_building.address != building.address:
                    # Если email занят, сообщаем об этом пользователю
                    flash('Корпус про данному адресу уже зарегистрирован!')
                    return redirect(url_for('edit_building'))
            building.address = form.address.data

            if form.photo.data:
                remove(path.join(app.root_path, building.photo))
                filename = f'building/{building.id}.{secure_filename(form.photo.data.filename)}'
                file_path = path.join(app.config['UPLOAD_FOLDER'], filename)
                form.photo.data.save(file_path)
                building.photo = file_path
            db.session.add(building)
            db.session.commit()
            return redirect(url_for('buildings'))

        return render_template('create_building.html', form=form, notification=True)
    else:
        return redirect(url_for('index'))


@app.route('/delete_building/<int:building_id>', methods=['GET', 'POST'])
@login_required
def delete_building(building_id):
    access = db.session.get(User, current_user.get_id())
    if access.role or access.id == access.id:
        remove(path.join(app.root_path, db.session.get(Building, building_id).photo))
        delete = db.session.get(Building, building_id)
        db.session.delete(delete)
        db.session.commit()
        return redirect(url_for('buildings'))


@app.route('/categorys', methods=['POST', 'GET'])
@login_required
def categorys():
    data = Category.query.order_by(Category.id).all()
    return render_template('categorys.html', data=data)


@app.route('/create_category', methods=['POST', 'GET'])
@login_required
def create_category():
    access = db.session.get(User, current_user.get_id())
    if access.role:
        form = AddCategoryForm()
        if form.validate_on_submit():
            # Запрашиваем в база пользователя по email
            is_address = Category.query.filter_by(name=form.name.data).first()
            if is_address:
                # Если email занят, сообщаем об этом пользователю
                flash('Категория с таким названием уже зарегистрирована!')
                return redirect(url_for('create_category'))
            category = Category(
                name=form.name.data
            )
            db.session.add(category)
            db.session.commit()
            return redirect(url_for('categorys'))
        return render_template('create_category.html', form=form, notification=True)
    else:
        return redirect(url_for('index'))


@app.route('/edit_category/<int:category_id>', methods=['POST', 'GET'])
@login_required
def edit_category(category_id):
    access = db.session.get(User, current_user.get_id())
    if access.role:
        category = db.session.get(Category, category_id)
        form = AddCategoryForm(name=category.name)
        if form.validate_on_submit():
            # Запрашиваем в база пользователя по email
            is_category = Building.query.filter_by(address=form.name.data).first()
            if is_category:
                if is_category.name != category.name:
                    # Если email занят, сообщаем об этом пользователю
                    flash('Корпус про данному адресу уже зарегистрирован!')
                    return redirect(url_for('edit_category'))
            category.name = form.name.data
            db.session.add(category)
            db.session.commit()
            return redirect(url_for('categorys'))

        return render_template('create_category.html', form=form, notification=True)
    else:
        return redirect(url_for('index'))


@app.route('/delete_category/<int:category_id>', methods=['GET', 'POST'])
@login_required
def delete_category(category_id):
    access = db.session.get(User, current_user.get_id())
    if access.role or access.id == access.id:
        delete = db.session.get(Category, category_id)
        db.session.delete(delete)
        db.session.commit()
        return redirect(url_for('categorys'))



@app.before_request
def create_bases():
    db.create_all()
    if not (User.query.filter_by(role=True).first()):
        db.session.add(
            User(
                email='admin@mail.ru',
                password=generate_password_hash('1234'),
                role=True
            )
        )


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_page'))


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?=next=' + request.url)
    return response
