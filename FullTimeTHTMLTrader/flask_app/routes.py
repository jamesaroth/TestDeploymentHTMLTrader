from flask import jsonify, request, render_template, url_for, redirect, session
from flask_app import app
from app import util, Account, view
from requests.exceptions import ConnectionError

UNAUTHORIZED = {"error": "unauthorized", "status_code": 401}
NOT_FOUND = {"error": "not found", "status_code": 404}
APP_ERROR = {"error": "application error", "status_code": 500}
BAD_REQUEST = {"error": "bad request", "status_code": 400}

@app.errorhandler(404)
def error404(e):
    return jsonify(NOT_FOUND), 404

@app.errorhandler(500)
def error500(e):
    return jsonify(APP_ERROR), 500

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        session['username'] = request.form['uname']
        session['password'] = util.hash_pass(request.form['pword'])
        account = Account.login(session['username'], session['password'])
        if account == None:
            return render_template('login.html', error=view.invalid_info())
        else:
            session['api_key'] = account.api_key
            return render_template('dashboard.html', Username=session['username'])

@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html', Username=session['username']) 

@app.route('/balance', methods=['GET'])
def balance():
    account = Account.api_authenticate(session['api_key'])
    if not account:
        return redirect(url_for('login'))
    cash = account.balance
    positions = account.get_positions()
    if len(positions) == 0:
        return render_template('balance.html', Title=view.bal_and_pos(cash) + " " + view.no_positions())
    else:
        bal = 0
        for position in positions:
            ticker = position.ticker
            shares = position.shares
            px = util.get_price(ticker)
            bal += px * shares
        return render_template('balance.html', Title=view.totbal(bal) + "\n" + view.totport(bal + cash), Title2=view.api_key(account.api_key))

@app.route('/price', methods=['GET', 'POST'])
def price():
    if request.method == 'GET':
        return render_template('ticker.html')
    elif request.method == 'POST':
        ticker = request.form['ticker']
        try:
            price = util.get_price(ticker)
            message = view.show_ticker_price(ticker, price)
        except ConnectionError:
            return render_template('ticker.html', message="Ticker not found please enter new valid ticker")
        return render_template('ticker.html', message=message)

@app.route('/positions', methods=['GET'])
def positions():
    account = Account.api_authenticate(session['api_key'])
    if not account:
        return redirect(url_for('login'))
    positions = account.get_positions()
    if len(positions) == 0:
        return render_template('positions.html', Title=view.no_positions())
    else:
        bal = 0
        textlist = []
        for position in positions:
            ticker = position.ticker
            shares = position.shares
            px = util.get_price(ticker)
            bal += px * shares
            textlist.append(view.stockbal(shares, ticker, px * shares))
        totals = view.totbal(bal)
        return render_template('positions.html', Total=totals, Title=textlist)

@app.route('/trades', methods=['GET'])
def trades():
    account = Account.api_authenticate(session['api_key'])
    if not account:
        return redirect(url_for('login'))
    trades = account.get_trades()
    if len(trades) == 0:
        return render_template('trades.html', Total=view.total_trades(0))
    else:
        totals = view.total_trades(len(trades))
        tradelist = []
        for trade in trades:
            tradelist.append(view.trade_detail(trade.volume, trade.ticker, trade.price, trade.price * trade.volume, trade.time))
        return render_template('trades.html', Total=totals, Title=tradelist)

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    account = Account.api_authenticate(session['api_key'])
    if not account:
        return redirect(url_for('login'))
    else:
        if request.method == 'GET':
            return render_template('deposit.html', balance=view.bal_and_pos(account.balance))
        else:
            amt = float(request.form['deposit_amount'])
            account.deposit(amt)
            return render_template('deposit.html', amt1=view.deposit_outp(amt), balance=view.bal_and_pos(account.balance))

@app.route('/buy', methods=['GET', 'POST'])
def buy():
    account = Account.api_authenticate(session['api_key'])
    if not account:
        return redirect(url_for('login'))
    else:
        if request.method == 'GET':
            return render_template('buy.html')
        else:
            ticker = request.form['tick_buy']
            shares = float(request.form['shareno_buy'])
            try:
                account.buy(ticker, shares)
                message = view.total_trades(1)
            except ConnectionError:
                return render_template('buy.html', error="Ticker not found please enter new valid ticker")
            except ValueError:
                return render_template('buy.html', error=view.insuf_funds())
            return render_template('buy.html', message=message)
#TODO
@app.route('/sell', methods=['GET', 'POST'])
def sell():
    account = Account.api_authenticate(session['api_key'])
    if not account:
        return redirect(url_for('login'))
    else:
        if request.method == 'GET':
            return render_template('sell.html')
        else:
            ticker = request.form['tick_sell']
            shares = float(request.form['shareno_sell'])
            try:
                account.sell(ticker, shares)
                message = view.total_trades(1)
            except ConnectionError:
                return render_template('sell.html', error="Ticker not found please enter new valid ticker")
            except ValueError:
                return render_template('sell.html', error=view.insuf_funds())
            return render_template('sell.html', message=message)

@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   session.pop('password', None)
   return redirect(url_for('login'))

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    account = Account.api_authenticate(session['api_key'])
    if not account:
        return redirect(url_for('login'))
    else:
        if request.method == 'GET':
            return render_template('reset.html')
        else:
            if request.form['pword'] != request.form['pword_confirm']:
                return render_template('reset.html', message="Passwords entered do not match.  Please re-enter a new password.")
            else:
                account.set_password(util.hash_pass(request.form['pword']))
                account.save()
                return render_template('reset.html', message="Password reset successful.")