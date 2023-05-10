from flask import Flask, render_template, request, redirect, url_for, session, escape, jsonify
from flask_pymongo import PyMongo
from flask import flash

app = Flask(__name__)

#session 사용하기위한 secret_key 
app.secret_key = 'software_engineering'

# MongoDB 연결 설정
app.config['MONGO_URI'] = 'mongodb+srv://peng2412:!jhy05744715@cluster0.qsv8zhv.mongodb.net/test'
mongo = PyMongo(app)

# 사용자 정보를 담을 MongoDB 컬렉션
users = mongo.db.users
history = mongo.db.trade_history

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
    if request.method=="POST":
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
            'password': password,
            'money' : 0,
            'coin' : 0
        }
        users.insert_one(post)

        # 회원가입 성공 메시지 출력 후 로그인 페이지로 이동
        return redirect(url_for('index'))


    # user 계좌 정보 불러오기.

# account는 원래 있는 정보를 받아서 사용하는 거니 (입력 x) GET 형식으로 받아야 함
@app.route('/account',methods=['GET'])
def account():
        # username=request.args.get('username')
        money_data=users.find_one({},{"money":1}) # username이 맞는 계정 불러오기
        coin_data=users.find_one({},{"coin":1}) # username이 맞는 계정 불러오기
        #mongodb find( , )에서 뒤에 필드 쓸 부분만 불러와서 in}t형으로 바꿔보자
        return render_template('account.html', money=money_data,coin=coin_data)

if __name__ == '__main__':
    app.run(debug=True) 
