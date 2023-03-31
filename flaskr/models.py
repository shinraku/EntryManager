""" DBのtable設計とCRUDメソッド群 """

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flaskr.views import app
from flask_bcrypt import generate_password_hash, check_password_hash
from datetime import datetime
import os

DB_URI = 'postgresql://postgres:PASSWORD@localhost/members'
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = 'SECRET'

db = SQLAlchemy(app)
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    """ LoginManagerをDBに対して動作させるためのメソッド """
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    """ ログインセッションを管理するUserテーブル """
    id = db.Column(db.Integer, primary_key=True) #DBにおけるid
    username = db.Column(db.String(32), index=True) #表示される名前
    userid = db.Column(db.String(32), index=True, unique=True) #ログイン時に使うid
    password = db.Column(db.Text) #パスワード
    status = db.Column(db.Text, default='退室') #在室状況
    degree_year = db.Column(db.String(4)) #年次(B3 ~ M2, D, OB)
    picture_path = db.Column(db.Text, nullable=True) #アイコン画像の保存先
    is_active = db.Column(db.Boolean, default=True)  # login_managerで必要
    create_at = db.Column(db.DateTime, default=datetime.now)  # datetime.now()では変になる
    update_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, username, userid, password, degree_year):
        """ ユーザ名、ユーザid、パスワード、年次が入力必須 """
        self.username = username
        self.userid = userid
        self.password = generate_password_hash(password).decode('utf-8')
        self.degree_year = degree_year

    def check_password(self, password):
        """ パスワードをチェックしてTrue/Falseを返す """
        return check_password_hash(self.password, password)

    def reset_password(self, password):
        """ 再設定されたパスワードをDBにアップデート """
        self.password = generate_password_hash(password).decode('utf-8')

    @classmethod
    def select_by_userid(cls, userid):
        """ UserテーブルからuseridでSELECTされたインスタンスを返す """
        return cls.query.filter(User.userid==userid).first()
    
    @classmethod
    def select_by_id(cls, id):
        """ UserテーブルからidでSELECTされたインスタンスを返す """
        return cls.query.get(id)

    @classmethod
    def select_by_entry(cls):
        """ Userテーブルからstatusが退室以外のインスタンスを返す """
        degrees = ['D', 'M2', 'M1', 'B4', 'B3']
        entry_user = []
        for d in degrees:
            entry_user.extend(cls.query.filter((User.status!='退室') & (User.degree_year==d)).order_by(User.id).all())
        return entry_user
    
    @classmethod
    def select_by_exit(cls):
        """ Userテーブルからstatusが退室のインスタンスを返す """
        degrees = ['D', 'M2', 'M1', 'B4', 'B3']
        exit_user = []
        for d in degrees:
            exit_user.extend(cls.query.filter((User.status=='退室') & (User.degree_year==d)).order_by(User.id).all())
        return exit_user