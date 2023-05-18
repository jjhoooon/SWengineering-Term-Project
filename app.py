from flask import Flask, render_template, request, redirect, url_for, session, escape, jsonify
from flask_pymongo import PyMongo
from flask import flash
import json

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

# signup이 url 패턴이 같은데도 괜찮은 이유
# => Flask에서는 동일한 URL 패턴을 사용하여 GET과 POST 요청을 구분하여 
#    처리할 수 있기 때문    

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


    # user 계좌 정보 불러오기
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
    app.run(debug=True) 

@app.route('/overview')
def overview():
    # history db를 이용
    # 테이블의 Last Price는 맨 처음에는 currentprice. 처음이니까 변화 없으니 change는 없음.
    # if (2번째 이상의 거래가 발생하면) currentprice는 recentprice가 되고 새 currentprice가 생김. 그 price를 Last Price에 넣기
    # 그 두 개의 차이를 %로 환산해서 테이블의 change로 함
    ht=history.find({})
    ht_json=json.dumps(ht)
    priceAndChange=dict()
    for history_field in ht:
        od=int(history_field['order'])
        cp=int(history_field['currentprice'])
        if od>=2: # 2번째 이상의 거래가 발생했다면
            previous_od=od-1
            previous_ht=history.find_one({'order':previous_od})
            # 이전 order의 currentprice = 현재 order의 recentprice
            rp=int(previous_ht['currentprice'])
            # 변화량 계산 , 소수점 아래 2자리 수 까지
            cg=round(float((cp-rp)/rp*100),2)
            priceAndChange[od]=[cp,cg] # currentprice가 같을 때를 대비해 order로 구분 짓고, value로 cp,cg를 list로 넣음
        else: # 맨 처음 거래 change가 없음
            priceAndChange[od]=[cp,0]
    
    return render_template('overview.html', ht=ht, ht_json=ht_json, priceAndChange=priceAndChange)

@app.route('/okoverview/<username>')
def okoverview(username):
    ht=history.find({})
    priceAndChange=dict()
    for history_field in ht:
        od=int(history_field['order'])
        cp=int(history_field['currentprice'])
        if od>=2: # 2번째 이상의 거래가 발생했다면
            previous_od=od-1
            previous_ht=history.find_one({'order':previous_od})
            # 이전 order의 currentprice = 현재 order의 recentprice
            rp=int(previous_ht['currentprice'])
            # 변화량 계산 , 소수점 아래 2자리 수 까지
            cg=round(float((cp-rp)/rp*100),2)
            priceAndChange[od]=[cp,cg] # currentprice가 같을 때를 대비해 order로 구분 짓고, value로 cp,cg를 list로 넣음
        else: # 맨 처음 거래 change가 없음
            priceAndChange[od]=[cp,0]
    return render_template('okoverview.html',username=username, ht=ht, priceAndChange=priceAndChange)

@app.route('/trading/<username>')
def trading(username):
    money_data=users.find_one({'username':username},{'money':1})
    coin_data=users.find_one({'username':username},{'coin':1})
    mk=market.find_one({})
    market_coin=int(mk['coin'])
    ps=post.find({})
    return render_template('trading.html',username=username, money=money_data, coin=coin_data, market_coin=market_coin, ps=ps)


@app.route('/market_trading/<username>', methods=['GET','POST'])
def market_trading(username):
    # def coin_trading() 함수로 로그인한 사용자의 coin 개수와 money 개수를 변경 
    # 그리고 render_template('trading.html')
    
    market_trading=int(request.form.get('market_trading'))
    
    # coin 개수가 0 이하로 잘못 입력했다면 오류 발생
    if market_trading<=0:
        flash('잘못 입력하셨습니다! 다시 입력해주세요')
        return redirect(url_for('trading',username=username))
    
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
    
    # overview를 위한 history collection update
    ht=list(history.find({}))
    if len(ht)>0: # 만약 거래 내역이 있다면
        # 새로운 거래 내역의 order = 이전 거래 내역 + 1. 
        # 즉, 가장 최신(가장 큰) order + 1
        od=int(max(ht, key=lambda x:x['order'])['order'])+1
    else: # 만약 거래 내역이 없다면
        od=1

    new_history={
        'order' : od,
        'currentprice' : 100
    }
    
    history.insert_one(new_history)
    
    # 마켓 보유 코인 update 해줘야 함
    # 원래 보유 코인 개수 - 구매한 코인 개수
    updated_market_coin= int(mk['coin'])-market_trading # 마켓 보유 코인 update 
    market.update_one({},{"$set":{'coin':updated_market_coin}})
    
    # 사용자의 coin과 money를 업데이트 해줘야 함
    # coin update => 현재 보유한 coin + 구매한 코인 개수
    # money update => 현재 보유한 money - (구매한 코인 개수 x 100) 
    # 마켓 코인은 100원이기 때문
    updated_coin=int(user['coin'])+market_trading
    updated_money=int(user['money'])-(market_trading*100)
    users.update_one({'username':username},{"$set":{'money':updated_money,'coin':updated_coin}})
    
    money_data=users.find_one({"username":username},{"money":1})
    coin_data=users.find_one({"username":username},{"coin":1})
    
    return render_template('trading.html',username=username,money=money_data,coin=coin_data,market_coin=updated_market_coin)

# url_for와 함수 이름 일치 시키자
@app.route('/posting/<username>')
def posting(username):
    return render_template('post.html',username=username)

@app.route('/post_up/<username>', methods=['POST'])
def post_up(username):
    coin_num = request.form['coin_num']
    coin_price = request.form['coin_price']
    
    # coin 개수와 가격이 0 이하로 잘못 입력했다면 오류 발생
    if int(coin_num)<=0 or int(coin_price)<=0:
        flash('잘못 입력하셨습니다! 다시 입력해주세요')
        return render_template('post.html',username=username)
    
    # 현재 사용자 정보 
    user = users.find_one({'username': username})
    
    # 현재 판매 게시글 현황
    ps=list(post.find({}))
    if len(ps)>0: # 만약 판매 게시글이 있다면
        # 새로운 게시글의 order = 이전 판매 게시글 + 1. 
        # 즉, 가장 최신(가장 큰) order + 1
        od=int(max(ps, key=lambda x:x['order'])['order'])+1
    else: # 만약 판매 게시글이 없다면
        od=1
    
    postup = {
        'order': od,
        'seller_username': user['username'],
        'coin_num': coin_num,
        'coin_price': coin_price,
    }
    
    post.insert_one(postup)
    
    return redirect(url_for('okindex',username=username))

@app.route('/purchase/<username>/<post_order>')
def purchase(username,post_order):
    ps=post.find_one({'order':int(post_order)}) # 여기서 post_order와 같은 order를 가진 post를 가져와야 한다
    seller=users.find_one({'username':ps['seller_username']}) # 여기선 판매자, 
    # 판매 게시글의 seller_username과 같은 username을 가진 user를 가져와야 한다
    consumer=users.find_one({'username':username}) # 여기선 구매자
    
    # 만약 구매자의 money가 coin_num*coin_price보다 작으면 오류
    if int(consumer['money'])<int(ps['coin_num'])*int(ps['coin_price']):
        flash("잔액이 부족합니다!")
        return redirect(url_for('trading',username=username))
    
    # 오류 없이 정상적으로 구매가 이루어진 경우
    
    seller_updated_money=int(seller['money'])+int(ps['coin_num'])*int(ps['coin_price']) # 판매자의 money를 게시글 수익만큼 증가
    seller_updated_coin=int(seller['coin'])-int(ps['coin_num'])
    
    consumer_updated_money=int(consumer['money'])-int(ps['coin_num'])*int(ps['coin_price']) # 구매자의 money를 게시글 수익만큼 감소
    consumer_updated_coin=int(consumer['coin'])+int(ps['coin_num']) # 구매자의 coin을 게시글의 coin 만큼 증가
    
    # 판매자 users update
    users.update_one({'username':ps['seller_username']},{"$set":{'money':seller_updated_money,'coin':seller_updated_coin}})
    
    # 구매자 users update
    users.update_one({'username':username},{"$set":{'money':consumer_updated_money,'coin':consumer_updated_coin}})
    
    # 구매한 post의 order보다 더 큰 order가 존재하면
    # 그 order를 가진 게시글들의 order를 한 칸씩 앞으로 밀어줘야 함
    # for문을 이용해 더 큰 order를 가진 게시글들을 찾기
    big_ps=post.find({})
    for big in big_ps:
        if big['order']>int(post_order): # post document들의 'order'는 이미 int형
            updated_big_order=big['order']-1
            post.update_one({'order':big['order']},{"$set":{'order':updated_big_order}})

    # 구매 완료 했으니 그 판매 게시글 없애기
    post.delete_one({'order':int(post_order)})
    
    # overview를 위한 history collection update
    ht=list(history.find({}))
    if len(ht)>0: # 만약 거래 내역이 있다면
        # 새로운 거래 내역의 order = 이전 거래 내역 + 1. 
        # 즉, 가장 최신(가장 큰) order + 1
        od=int(max(ht, key=lambda x:x['order'])['order'])+1
    else: # 만약 거래 내역이 없다면
        od=1
    
    new_history={
        'order' : od,
        'currentprice' : int(ps['coin_price'])
    }
    
    history.insert_one(new_history)
    
    return redirect(url_for('trading',username=username))


# 구매자 username == 판매자 username 이면 구매 버튼 대신 삭제 버튼 나타나게 해야 함
@app.route('/delete_post/<username>/<post_order>')
def delete_post(username,post_order):
    big_ps=post.find({})
    # 삭제한 post의 order보다 더 큰 order가 존재하면
    # 그 order를 가진 게시글들의 order를 한 칸씩 앞으로 밀어줘야 함
    # for문을 이용해 더 큰 order를 가진 게시글들을 찾기
    for big in big_ps:
        if big['order']>int(post_order): # post document들의 'order'는 이미 int형
            updated_big_order=big['order']-1
            post.update_one({'order':big['order']},{"$set":{'order':updated_big_order}})

    post.delete_one({'order':int(post_order)}) # 여기서 post_order와 같은 order를 가진 post를 가져와야 한다
    return redirect(url_for('trading',username=username))