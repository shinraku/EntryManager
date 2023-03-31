from wtforms.form import Form
from wtforms.fields import (
    IntegerField, StringField, TextAreaField, PasswordField,
    HiddenField, SubmitField, FileField, RadioField, SelectField
)
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from flaskr.views import User


class LoginForm(Form):
    """ログインフォームのテンプレート"""
    userid = StringField('ユーザID', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[DataRequired()])

    submit = SubmitField('ログイン')

    def validate_password(self, field):
        if len(field.data) < 4:
            raise ValidationError('パスワードは4文字以上で！')

class ForgotPassForm(Form):
    """パスワード再設定フォームのテンプレート"""
    userid = StringField('ユーザID', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[DataRequired()])
    conf_password = PasswordField('確認用パスワード', validators=[DataRequired(), EqualTo('password', message='元のパスワードと一致しません')])

    submit = SubmitField('ログイン')

    def validate_password(self, field):
        if len(field.data) < 4:
            raise ValidationError('パスワードは4文字以上で！')

class RegisterForm(Form):
    """新規登録フォームのテンプレート"""
    username = StringField('ユーザ名(表示名)', validators=[DataRequired()])
    userid = StringField('ユーザID', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[DataRequired()])
    conf_password = PasswordField('確認用パスワード', validators=[DataRequired(), EqualTo('password', message='元のパスワードと一致しません')])
    degree_year = SelectField('年次',choices=[('B3', 'B3'), ('B4', 'B4'), ('M1', 'M1'), ('M2', 'M2'), ('D', 'D')])

    submit = SubmitField('ユーザ登録')

    def validate_userid(self, field):
        if User.select_by_userid(field.data):
            raise ValidationError('すでに登録されているIDです')

class StatusForm(Form):
    """ステータス変更フォームのテンプレート"""
    status = RadioField(choices=[('在室', '在室'), ('離席', '離席'), ('退室', '退室'), ('other', 'その他')], validators=[DataRequired()])
    othertext = StringField('その他のステータス')

    submit = SubmitField('更新')

class SettingForm(Form):
    """設定フォームのテンプレート"""
    username = StringField('ユーザ名')
    degree_year = SelectField('年次', choices=[('B3', 'B3'), ('B4', 'B4'), ('M1', 'M1'), ('M2', 'M2'), ('D', 'D'), ('OB', 'OB')])
    picture_path = FileField('アイコン画像')

    submit = SubmitField('更新')