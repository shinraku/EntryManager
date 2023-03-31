from flask import (
    Flask, render_template, request, redirect, url_for, flash, 
)
from flask_login import login_required, login_user, logout_user, current_user
from datetime import datetime

app = Flask(__name__)
from flaskr.models import db, User
from flaskr.forms import (
    ForgotPassForm, LoginForm, RegisterForm, SettingForm, StatusForm
)
import contextlib
from PIL import Image
import os

@contextlib.contextmanager
def transaction(session):
    if not session.in_transaction():
        with session.begin():
            yield
    else:
        yield

@app.route('/', methods=['GET'])
def index():
    """入退室者をそれぞれ取得し、一覧表示"""
    entry_user = User.select_by_entry()
    exit_user = User.select_by_exit()
    return render_template('index.html', entry_user=entry_user, exit_user=exit_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ログイン用の画面"""
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        userid = form.userid.data
        password = form.password.data
        user = User.select_by_userid(userid)
        if user and user.check_password(password):
            """ ユーザに対してログイン処理を施す """
            login_user(user)
            return redirect(url_for('index'))
        elif user:
            flash('パスワードが間違っています')
        else:
            flash('存在しないユーザです')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """新規登録用の画面"""
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        userid = form.userid.data
        password = form.password.data
        degree_year = form.degree_year.data
        user = User(username, userid, password, degree_year)
        with transaction(db.session()):
            db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """ パスワード再設定用の画面 """
    form = ForgotPassForm(request.form)
    user = None
    if request.method == 'POST':
        userid = form.userid.data
        print(userid)
        user = User.select_by_userid(userid)
        print(user)
        if not user: #userが見つからなかったら
            flash('存在しないユーザーです')
        elif form.password.data:
            with transaction(db.session()):
                user.reset_password(form.password.data)
            db.session.commit()
            return redirect(url_for('login'))
        return render_template('forgot_password.html', form=form, user=user)
    return render_template('forgot_password.html', form=form, user=user)


@app.route('/logout')
@login_required
def logout():
    """ログアウトする"""
    logout_user()
    return redirect(url_for('index'))


@app.route('/status', methods=['GET', 'POST'])
@login_required
def status():
    """ステータス変更用の画面"""
    form = StatusForm(request.form)
    statuses = ['在室', '離席', '退室']
    current_status = current_user.status
    #現在のステータスをラジオボタンとテキストボックスのデフォルトにする
    if current_status in statuses: #現在のステータスが"その他"以外
        form.status.default = current_status
    else:
        form.status.default = 'other'
        form.othertext.default = current_status

    user_id = current_user.get_id()
    if request.method == 'POST':
        user = User.select_by_id(user_id)
        with transaction(db.session()):
            substatus = form.status.data
            if substatus == 'other':
                if form.othertext.data == '':
                    flash('ステータスを入力してください')
                    return render_template('status.html', form=form)
                user.status = form.othertext.data
            else:
                user.status = substatus
        db.session.commit()
        return redirect(url_for('index'))
    form.process() #デフォルト値反映(ここじゃないとうまく動かない)
    return render_template('status.html', form=form)

@app.route('/setting', methods=['GET', 'POST'])
@login_required
def setting():
    """設定用の画面"""
    form = SettingForm(request.form)
    form.degree_year.default = current_user.degree_year
    user_id = current_user.get_id()
    if request.method == 'POST':
        user = User.select_by_id(user_id)
        with transaction(db.session()):
            name = form.username.data
            if name:
                user.username = form.username.data
            user.degree_year = form.degree_year.data
            user.update_at = datetime.now()
            # fileの中身を読込
            file = request.files[form.picture_path.name].read()
            if file:
                os.remove('flaskr/static/' + user.picture_path)
                file_name = user_id + '_' + str(int(datetime.now().timestamp())) + '.jpg'
                picture_path = 'flaskr/static/user_images/' + file_name
                # picture_pathの箱にfileの中身を書き込む
                open(picture_path, 'wb').write(file)
                #書き込んだものを再呼び出して、画質を落と(圧縮)して書き込み
                img = Image.open(picture_path)
                img.save(picture_path, quality=30)
                user.picture_path = 'user_images/' + file_name
        db.session.commit()
        return redirect(url_for('index'))
    form.process()
    return render_template('setting.html', form=form)