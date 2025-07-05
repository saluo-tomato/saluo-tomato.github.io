from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):  # 继承 UserMixin
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    is_active = db.Column(db.Boolean, default=True)  # 用户是否激活

    # 与 Note 的一对多关系
    notes = db.relationship('Note', back_populates='user', cascade="all, delete-orphan")

    def set_password(self, password):
        """设置密码并加密"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """检查密码是否正确"""
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        """返回用户的唯一标识符，Flask-Login需要此方法"""
        return str(self.id)

    def __repr__(self):
        return f'<User {self.username}>'

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # 设置与 User 的关系，便于查询当前笔记的所属用户
    user = db.relationship('User', back_populates='notes')

    def __repr__(self):
        return f'<Note {self.title}>'

# 创建数据库和表格
def create_db(app):
    """创建数据库，确保在应用上下文中运行"""
    with app.app_context():
        db.create_all()
