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
history = mongo.db.history
market = mongo.db.market
post = mongo.db.post

@app.route('/logout')
def logout():
    session.clear()
    #flash("로그아웃 하였습니다.")
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/okindex/<username>')
def okindex(username):
    return render_template('okindex.html',username=username)

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
    return redirect(url_for('okindex',username=username))

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/post')
def post():
    return render_template('post.html')

@app.route('/post/<username>', methods=['GET','POST'])
def post_up(username):
    coin_num = request.form['coin_num']
    coin_price = request.form['coin_price']
    
    #현재 사용자 정보 
    # user = users.find_one({'username': username})
    
    postup = {
        'seller_username': username,
        'coin_num': coin_num,
        'coin_price': coin_price,
        'consumer_username' : "",
    }
    
    post.insert_one(postup)
    
    return redirect(url_for('okindex',username=username))
    

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
        'password': password,
        'money' : 0,
        'coin' : 0
    }
    users.insert_one(post)

    # 회원가입 성공 메시지 출력 후 로그인 페이지로 이동
    return redirect(url_for('index'))


    # user 계좌 정보 불러오기.
@app.route('/account/<username>',methods=['GET'])
def account(username): # url로 부를 때 <username>을 받아오는 걸로 해보자!
        # 근데 이제 회원 정보에 맞는 money와 coin을 구해야함
        # 이 때 회원 정보에 맞는 document만 찾고 싶을 땐 find_one을 사용해야 함
        money_data=users.find_one({"username":username},{"money":1}) # username이 맞는 계정 불러오기
        coin_data=users.find_one({"username":username},{"coin":1}) # username이 맞는 계정 불러오기
        #mongodb find( , )에서 뒤에 필드 쓸 부분만 불러와서 in}t형으로 바꿔보자
        return render_template('account.html', money=money_data,coin=coin_data,username=username)

    #입금 시, 잔액 업데이트
@app.route('/update_money/<username>', methods=['GET','POST'])    
def update_money(username):
    
    new_money = int(request.form.get('new_money'))
    
    #mongoDB에서 해당 사용자의 money 값 가져오기
    user = users.find_one({'username': username})
    current_money = int(user['money'])
    
    #새로운 money 값 계산
    updated_money = current_money + new_money
    
    #mongoDB에 해당 사용자 money 값 업데이트
    users.update_one({'username':username},{"$set":{"money": updated_money}})
    
    money_data=users.find_one({"username":username},{"money":1}) # username이 맞는 계정 불러오기
    coin_data=users.find_one({"username":username},{"coin":1}) # username이 맞는 계정 불러오기
    
    return render_template('account.html', money=money_data,coin=coin_data,username=username)

    #출금 시, 잔액 업데이트

@app.route('/withdraw_money/<username>', methods=['GET','POST'])
def withdraw_money(username):
    
    new_money = int(request.form.get('new_money'))
    
    money_data=users.find_one({"username":username},{"money":1})
    coin_data=users.find_one({"username":username},{"coin":1})
    
    user = users.find_one({'username':username})
    current_money = int(user['money'])
    
    #새로운 money 값 계산
    updated_money = current_money - new_money
    
    if updated_money < 0:
        flash("출금하기 위한 잔액이 부족합니다.")
        return render_template('account.html',username=username,money=money_data,coin=coin_data)     
    
    #money 업데이트
    users.update_one({'username':username},{"$set":{"money": updated_money}})
    
    money_data=users.find_one({"username":username},{"money":1})
    coin_data=users.find_one({"username":username},{"coin":1})
    
    return render_template('account.html', money=money_data,coin=coin_data,username=username)    

    

if __name__ == '__main__':
    

#현재 에러 발생!! (2가지를 고려해봐야함)
#1. account.html 에서 username과 input값을 flask에 제대로 전송했는지
#2. flask, '/update_money'에서 mongodb의 money_field 업데이트 코드가 맞는지
#추가적으로, 2번에서 html에서 받은 데이터 타입과 DB의 데이터 타입을 생각해봐야함!
    app.run(debug=True) 

@app.route('/overview/<username>')
def overview(username):
    return render_template('overview.html',username=username)

@app.route('/trading/<username>')
def trading(username):
    money_data=users.find_one({'username':username},{'money':1})
    coin_data=users.find_one({'username':username},{'coin':1})
    mk=market.find_one({})
    market_coin=int(mk['coin'])
    return render_template('trading.html',username=username, money=money_data, coin=coin_data, market_coin=market_coin)


@app.route('/market_trading/<username>', methods=['GET','POST'])
def market_trading(username):
    # def coin_trading() 함수로 로그인한 사용자의 coin 개수와 money 개수를 변경 
    # 그리고 render_template('trading.html')
    
    market_trading=int(request.form.get('market_trading'))
    
    mk=market.find_one({}) # market 정보 불러오기
    user = users.find_one({'username':username}) # 로그인한 사용자 찾기
    
    # 마켓 코인 < 구매할 코인 이면 오류 발생 시켜야 함
    if int(mk['coin'])<market_trading:
        flash("구매할 코인 개수가 마켓이 보유한 코인을 초과하였습니다")
        return redirect(url_for('trading',username=username))
    
    # 구매 금액 > 잔액 이면 오류 발생 시켜야 함
    if int(user['money'])<(market_trading*100):
        flash("잔액이 부족합니다")
        return redirect(url_for('trading',username=username))
    
    # 오류 발생이 없을 경우
    
    # 마켓 보유 코인 update 해줘야 함
    # 원래 보유 코인 개수 - 구매한 코인 개수
    updated_market_coin= int(mk['coin'])-market_trading # 마켓 보유 코인 update 
    market.update_one({},{"$set":{'coin':updated_market_coin}})
    
    # 사용자의 coin과 money를 업데이트 해줘야 함
    # coin update => 현재 보유한 coin + 구매한 코인 개수
    # money update => 현재 보유한 money - (구매한 코인 개수 x 100) 
    # 마켓 코인은 100원이기 때문!
    updated_coin=int(user['coin'])+market_trading
    updated_money=int(user['money'])-(market_trading*100)
    users.update_one({'username':username},{"$set":{'money':updated_money,'coin':updated_coin}})
    
    money_data=users.find_one({"username":username},{"money":1})
    coin_data=users.find_one({"username":username},{"coin":1})
    
    return render_template('trading.html',username=username,money=money_data,coin=coin_data,market_coin=updated_market_coin)

