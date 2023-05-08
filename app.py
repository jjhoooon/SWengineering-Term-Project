from flask import Flask, render_template, request, redirect, url_for, session, escape
from flask_pymongo import PyMongo
from flask import flash

app = Flask(__name__)
#111
#session 사용하기위한 secret_key 
app.secret_key = 'software_engineering'

# MongoDB 연결 설정
app.config['MONGO_URI'] = 'mongodb+srv://peng2412:!jhy05744715@cluster0.qsv8zhv.mongodb.net/test'
mongo = PyMongo(app)

# 사용자 정보를 담을 MongoDB 컬렉션
users = mongo.db.users

@app.route('/logout')
def logout():
    session.clear()
    #flash("로그아웃 하였습니다.")
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/okindex')
def okindex():
    return render_template('okindex.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']

    # MongoDB에서 사용자 정보 조회
    user = users.find_one({'username': username, 'password': password})

    # 사용자 정보가 없으면 로그인 실패
    if user is None:
        flash('Username과 Password를 다시 확인해주세요.')
        return redirect(url_for('login'))

    # 사용자 정보가 있으면 로그인 성공
    # return 'Welcome, {}'.format(username)
    return redirect(url_for('okindex'))

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    username = request.form['username']
    password = request.form['password']

    # MongoDB에서 이미 등록된 사용자인지 확인
    user = users.find_one({'username': username})
    if user:
        flash('이미 사용중인 username입니다')
        return redirect(url_for('signup'))

    # 사용자 정보를 MongoDB에 등록
    post = {
        'username': username,
        'password': password
    }
    users.insert_one(post)

    # 회원가입 성공 메시지 출력 후 로그인 페이지로 이동
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True) 
