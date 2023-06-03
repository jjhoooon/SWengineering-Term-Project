from flask import Flask, render_template, request, redirect, url_for, session, escape, jsonify
from flask_pymongo import PyMongo
from flask import flash

app = Flask(__name__)

app.secret_key = 'software_engineering'

app.config['MONGO_URI'] = 'mongodb+srv://peng2412:!jhy05744715@cluster0.qsv8zhv.mongodb.net/test'
mongo = PyMongo(app)

users = mongo.db.users
history = mongo.db.history
market = mongo.db.market
post = mongo.db.post

@app.route('/logout')
def logout():
    session.clear()
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

    user = users.find_one({'username': username, 'password': password})

    if user is None:
        flash('Username과 Password를 다시 확인해주세요.')
        return redirect(url_for('login'))

    return redirect(url_for('okindex',username=username))

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    
    if password != confirm_password:
        flash('비밀번호가 일치하지 않습니다.')
        return redirect(url_for('signup'))

    user = users.find_one({'username': username})
    if user:
        flash('이미 사용중인 username입니다')
        return redirect(url_for('signup'))

    post = {
        'username': username,
        'password': password,
        'money' : 0,
        'coin' : 0
    }
    users.insert_one(post)
    
    return redirect(url_for('index'))



@app.route('/account/<username>',methods=['GET'])
def account(username):
        money_data=users.find_one({"username":username},{"money":1}) 
        coin_data=users.find_one({"username":username},{"coin":1}) 
        
        return render_template('account.html', money=money_data,coin=coin_data,username=username)
    
if __name__ == '__main__':


@app.route('/update_money/<username>', methods=['GET','POST'])    
def update_money(username):
    
    new_money = int(request.form.get('new_money'))
    
    user = users.find_one({'username': username})
    current_money = int(user['money'])
    
    updated_money = current_money + new_money

    users.update_one({'username':username},{"$set":{"money": updated_money}})
    
    money_data=users.find_one({"username":username},{"money":1}) 
    coin_data=users.find_one({"username":username},{"coin":1}) 
    
    return render_template('account.html', money=money_data,coin=coin_data,username=username)

@app.route('/withdraw_money/<username>', methods=['GET','POST'])
def withdraw_money(username):
    
    new_money = int(request.form.get('new_money'))
    
    money_data=users.find_one({"username":username},{"money":1})
    coin_data=users.find_one({"username":username},{"coin":1})
    
    user = users.find_one({'username':username})
    current_money = int(user['money'])

    updated_money = current_money - new_money
    
    if updated_money < 0:
        flash("출금하기 위한 잔액이 부족합니다.")
        return render_template('account.html',username=username,money=money_data,coin=coin_data)     
    
    users.update_one({'username':username},{"$set":{"money": updated_money}})
    
    money_data=users.find_one({"username":username},{"money":1})
    coin_data=users.find_one({"username":username},{"coin":1})
    
    return render_template('account.html', money=money_data,coin=coin_data,username=username)    

@app.route('/overview', methods=['GET','POST'])
def overview():
    ht=history.find({})
    priceAndChange=dict()
    for history_field in ht:
        od=int(history_field['order'])
        cp=int(history_field['currentprice'])
        if od>=2:
            previous_od=od-1
            previous_ht=history.find_one({'order':previous_od})

            rp=int(previous_ht['currentprice'])
            cg=round(float((cp-rp)/rp*100),2)
            priceAndChange[od]=[cp,cg]
        else:
            priceAndChange[od]=[cp,0]
    
    order_list = history.find({},{'order':1})
    price_list = history.find({},{'currentprice':1})
    
    orders = [str(d.get('order')) for d in order_list]
    prices = [str(d.get('currentprice')) for d in price_list]

    return render_template('overview.html', history=ht, priceAndChange=priceAndChange, orders=orders, prices=prices)

@app.route('/okoverview/<username>', methods=['GET','POST'])
def okoverview(username):
    ht=history.find({})
    priceAndChange=dict()
    for history_field in ht:
        od=int(history_field['order'])
        cp=int(history_field['currentprice'])
        if od>=2:
            previous_od=od-1
            previous_ht=history.find_one({'order':previous_od})
            rp=int(previous_ht['currentprice'])
            cg=round(float((cp-rp)/rp*100),2)
            priceAndChange[od]=[cp,cg]
            priceAndChange[od]=[cp,0]
         
    order_list = history.find({},{'order':1})
    price_list = history.find({},{'currentprice':1})
    
    orders = [str(d.get('order')) for d in order_list]
    prices = [str(d.get('currentprice')) for d in price_list]
    
    return render_template('okoverview.html',username=username, history=ht, priceAndChange=priceAndChange, orders=orders, prices=prices)

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
    market_trading=int(request.form.get('market_trading'))

    if market_trading<=0:
        flash('잘못 입력하셨습니다! 다시 입력해주세요')
        return redirect(url_for('trading',username=username))
    
    mk=market.find_one({})
    user = users.find_one({'username':username})
    
    if int(mk['coin'])<market_trading:
        flash("구매할 코인 개수가 마켓이 보유한 코인을 초과하였습니다")
        return redirect(url_for('trading',username=username))
    

    if int(user['money'])<(market_trading*100):
        flash("잔액이 부족합니다")
        return redirect(url_for('trading',username=username))

    ht=list(history.find({}))
    if len(ht)>0:
        od=int(max(ht, key=lambda x:x['order'])['order'])+1
    else:
        od=1

    new_history={
        'order' : od,
        'currentprice' : 100
    }
    
    history.insert_one(new_history)
    
    updated_market_coin= int(mk['coin'])-market_trading 
    market.update_one({},{"$set":{'coin':updated_market_coin}})

    updated_coin=int(user['coin'])+market_trading
    updated_money=int(user['money'])-(market_trading*100)
    users.update_one({'username':username},{"$set":{'money':updated_money,'coin':updated_coin}})
    
    return redirect(url_for('trading',username=username))

@app.route('/posting/<username>')
def posting(username):
    return render_template('post.html',username=username)

@app.route('/post_up/<username>', methods=['POST'])
def post_up(username):
    coin_num = request.form['coin_num']
    coin_price = request.form['coin_price']
    
    if int(coin_num)<=0 or int(coin_price)<=0:
        flash('잘못 입력하셨습니다! 다시 입력해주세요')
        return render_template('post.html',username=username)
    
    user = users.find_one({'username': username})
    
    if int(coin_num)<=0 or int(coin_price)<=0 or user['coin']<int(coin_num):
        flash('잘못 입력하셨습니다! 다시 입력해주세요')
        return render_template('post.html',username=username)
    
    ps=list(post.find({}))
    if len(ps)>0:
        od=int(max(ps, key=lambda x:x['order'])['order'])+1
    else:
        od=1

    postup = {
        'order': od,
        'seller_username': user['username'],
        'coin_num': coin_num,
        'coin_price': coin_price,
    }
    
    post.insert_one(postup)
    
    return redirect(url_for('trading',username=username))

@app.route('/purchase/<username>/<post_order>')
def purchase(username,post_order):
    ps=post.find_one({'order':int(post_order)})
    seller=users.find_one({'username':ps['seller_username']}) 
    consumer=users.find_one({'username':username})
    
    if int(consumer['money'])<int(ps['coin_num'])*int(ps['coin_price']):
        flash("잔액이 부족합니다!")
        return redirect(url_for('trading',username=username))
    
    seller_updated_coin=int(seller['coin'])-int(ps['coin_num'])
    seller_updated_money=int(seller['money'])+int(ps['coin_num'])*int(ps['coin_price'])
    
    consumer_updated_money=int(consumer['money'])-int(ps['coin_num'])*int(ps['coin_price']) 
    consumer_updated_coin=int(consumer['coin'])+int(ps['coin_num']) 
    
    users.update_one({'username':ps['seller_username']},{"$set":{'money':seller_updated_money,'coin':seller_updated_coin}})
    
    users.update_one({'username':username},{"$set":{'money':consumer_updated_money,'coin':consumer_updated_coin}})

    big_ps=post.find({})
    for big in big_ps:
        if big['order']>int(post_order):
            updated_big_order=big['order']-1
            post.update_one({'order':big['order']},{"$set":{'order':updated_big_order}})

    post.delete_one({'order':int(post_order)})
    
    ht=list(history.find({}))
    if len(ht)>0:

        od=int(max(ht, key=lambda x:x['order'])['order'])+1
    else: 
        od=1
    
    new_history={
        'order' : od,
        'currentprice' : int(ps['coin_price'])
    }
    
    history.insert_one(new_history)
    
    return redirect(url_for('trading',username=username))


@app.route('/delete_post/<username>/<post_order>')
def delete_post(username,post_order):
    big_ps=post.find({})

    for big in big_ps:
        if big['order']>int(post_order): 
            updated_big_order=big['order']-1
            post.update_one({'order':big['order']},{"$set":{'order':updated_big_order}})

    post.delete_one({'order':int(post_order)})
    return redirect(url_for('trading',username=username))
