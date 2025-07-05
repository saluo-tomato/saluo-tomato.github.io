from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Note, create_db

# 初始化Flask应用和LoginManager
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'  # 数据库路径
app.config['SECRET_KEY'] = 'your-secret-key'  # 用于Session管理
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 禁用SQLALCHEMY_TRACK_MODIFICATIONS警告
db.init_app(app)

# 初始化LoginManager
login_manager = LoginManager(app)
login_manager.login_view = "login"

# 用户加载
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 创建数据库
with app.app_context():  # 确保在应用上下文中创建数据库
    create_db(app)  # 这里直接调用，传递 app 参数

# 首页
@app.route('/')
def index():
    return render_template('index.html')

# 注册页
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username)
        user.set_password(password)  # 设置加密密码
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# 登录页
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):  # 使用加密的密码验证
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html')

# 登出
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# 用户主页，展示笔记
@app.route('/dashboard')
@login_required
def dashboard():
    notes = Note.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', notes=notes)

# 创建新笔记
@app.route('/create_note', methods=['GET', 'POST'])
@login_required
def create_note():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        note = Note(title=title, content=content, user_id=current_user.id)
        db.session.add(note)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('create_note.html')

# 编辑笔记
@app.route('/edit_note/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_note(id):
    note = Note.query.get_or_404(id)
    if note.user_id != current_user.id:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        note.title = request.form['title']
        note.content = request.form['content']
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('edit_note.html', note=note)

# 删除笔记
@app.route('/delete_note/<int:id>', methods=['GET'])
@login_required
def delete_note(id):
    note = Note.query.get_or_404(id)
    if note.user_id != current_user.id:
        return redirect(url_for('dashboard'))
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for('dashboard'))

# 运行应用
if __name__ == '__main__':
    app.run(debug=True)
