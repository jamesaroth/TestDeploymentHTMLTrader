import sys
import os
import requests
from app import view
from app import util
from app.account import Account

def login_menu():
    while True:
        try:
            user_input = view.login_menu()
            if int(user_input) == 3:
                view.program_end()
                sys.exit()
            elif int(user_input) == 2:
                username = view.username_inpt()
                pwd = util.hash_pass(view.password_inpt())
                user = Account.login(username, pwd)
                if user == None:
                    view.invalid_info()
                    return login_menu()
                return user
            elif int(user_input) == 1:
                user = Account()
                user.username = view.username_inpt()
                user.set_password(util.hash_pass(view.set_password_inpt()))
                user.balance = view.deposit_inpt()
                user.save()
                view.acc_created(user.username)
                return user
        except ValueError:
            view.choose_valid()
        
def main_menu_ctrl(user):
    while True:
        input()
        os.system("clear")
        answer = view.main_menu(user.username)
        if int(answer) == 9:
            view.program_end()
            return None
        elif int(answer) == 8:
            user.set_password(util.hash_pass(view.set_password_inpt()))
            user.save()
            view.saving_change()
        elif int(answer) == 7:
            trades = user.get_trades()
            view.total_trades(len(trades))
            for trade in trades:
                view.trade_detail(trade.volume, trade.ticker, trade.price, trade.price * trade.volume, trade.time)
        elif int(answer) == 6:
            positions = user.get_positions()
            if len(positions) == 0:
                view.no_positions()
            else:
                bal = 0
                for position in positions:
                    ticker = position.ticker
                    shares = position.shares
                    px = util.get_price(ticker)
                    bal += px * shares
                    view.stockbal(shares, ticker, px * shares)
                view.totbal(bal)
        elif int(answer) == 5:
            val_ord = True
            while val_ord == True:
                ticker = view.ask_ticker()
                px = float(util.get_price(ticker))
                view.show_ticker_price(ticker, px)
                if user.get_position_for(ticker).shares != 0:
                    shares = view.ask_num_shares()
                    try: 
                        y_n = view.confirm_order("sell", ticker, shares, px*shares)
                        if y_n == "y" or "Y":
                            user.sell(ticker, shares)
                            view.total_trades(1)
                            val_ord = False
                        else:
                            view.choose_valid()
                            val_ord = True
                    except ValueError:
                        view.insuf_funds()
                        val_ord = True
                else:
                    view.no_position_stock()
        elif int(answer) == 4:
            val_ord = True
            while val_ord == True:
                ticker = view.ask_ticker()
                px = float(util.get_price(ticker))
                view.show_ticker_price(ticker, px)
                view.bal_and_pos(user.balance)
                shares = view.ask_num_shares()
                try: 
                    y_n = view.confirm_order("buy", ticker, shares, px*shares)
                    if y_n == "y" or "Y":
                        user.buy(ticker, shares)
                        view.total_trades(1)
                        val_ord = False
                    else:
                        view.choose_valid()
                        val_ord = True
                except ValueError:
                    view.insuf_funds()
                    val_ord = True
        elif int(answer) == 3:
            amt = view.deposit_inpt()
            user.deposit(amt)
            view.deposit_outp(amt)
            view.newbalance_statement(user.balance)
        elif int(answer) == 2:
            x = True
            while x == True:
                ticker = view.ask_ticker()
                try:
                    px = util.get_price(ticker)
                    view.show_ticker_price(ticker, px)
                    x = False
                except requests.ConnectionError:
                    view.choose_valid()
        elif int(answer) == 1:
            view.api_key(user.api_key)
            view.bal_and_pos(user.balance)
            positions = user.get_positions()
            if len(positions) == 0:
                view.no_positions()
            else:
                bal = 0
                for position in positions:
                    ticker = position.ticker
                    shares = position.shares
                    px = util.get_price(ticker)
                    bal += px * shares
                view.totbal(bal)
                view.totport(bal + user.balance)
        else:
            view.choose_valid()
            

def run():
    while True:
        view.welcome()    
        user = login_menu()
        if not user:
            break
        main = main_menu_ctrl(user)
        if main == None:
            pass


