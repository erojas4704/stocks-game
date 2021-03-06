"""Flask app 24.5"""
from flask import Flask, send_from_directory, request, redirect, render_template, flash, jsonify, session, g 
from flask_debugtoolbar import DebugToolbarExtension
from models import User, connect_db, db, Game, Player, Stock, PlayerStock, Message, PlayerHistory
#from forms import RegisterUserForm, LoginForm, FeedbackForm, PasswordForm
from flask_sqlalchemy import SQLAlchemy
from forms import RegisterForm, LoginForm, NewGameForm
from sqlalchemy.exc import IntegrityError
from utils import format_money, get_money_class, get_ordinal, seconds_to_english
from dotenv import load_dotenv
import helpers
import market
import game
import os
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy').setLevel(logging.ERROR)
logging.getLogger('werkzeug').setLevel(logging.ERROR)

load_dotenv()
app = Flask(__name__)


app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
CURR_USER_KEY = "user_key"

connect_db(app)

app.jinja_env.globals['format_money'] = format_money
app.jinja_env.globals['get_money_class'] = get_money_class
app.jinja_env.globals['get_ordinal'] = get_ordinal
app.jinja_env.globals['seconds_to_english'] = seconds_to_english

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        user = User.query.get(session[CURR_USER_KEY])
        if user:
            g.user = user
        else:
            g.user = None
            del session[CURR_USER_KEY]
            flash("Invalid user")
            return redirect("/")
    else:
        g.user = None
    

@app.route('/css/<path:path>')  
def send_css(path):
    """CSS Subdir"""
    return send_from_directory('css', path,mimetype='text/css')
    
@app.route('/js/<path:path>')  
def send_js(path):
    """JS Subdir"""
    return send_from_directory('js', path,mimetype='text/js')

@app.route('/')
def send_index():
    """Landing Page"""
    add_user_to_g()
    
    return render_template("index.html", user = g.user)
    

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """ User login form """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(form.email.data, form.password.data)
        if user:
            login_user(user)
            return redirect('/')
        else:
            flash("Invalid e-mail or password!")

    return render_template("login.html", form=form)

@app.route('/games', methods=['GET'])
def games_page():
    public_games = Game.query.filter(Game.password == None).all()
    return render_template("games.html", user = g.user, public_games = public_games)

@app.route('/newgame', methods=['GET', 'POST'])
def new_game_form():
    form = NewGameForm()

    if form.validate_on_submit():
        game = Game.generate_game()

        game.host_id = g.user.id

        form.populate_obj(game)
        db.session.add(game)
        db.session.commit()
        return redirect(f'/games/{game.id}/join', 307)
        
    return render_template("newgame.html", form=form)

@app.route('/games/<game_id>/join', methods=['POST'])
def join_game(game_id):
    """Attempt to join the game. """
    game = Game.query.get(game_id)
    if game:
        game.add_player(g.user)
        return redirect(f'/games/{game.id}')
    
    flash("Invalid game session.")
    return redirect('/games')

@app.route('/games/<game_id>', methods=['GET'])
def view_game(game_id):
    """View Game Page"""
    game = Game.query.get(game_id)
    
    if game:
        game.players.sort(key = helpers.placement_sort, reverse = True)
        return render_template('game.html', user = g.user, game = game)

    flash("Invalid game session.")
    return redirect('/games')
        
@app.route('/games/<int:game_id>/stocks', methods=['GET'])
def view_stocks(game_id):
    """Stock listings for a game."""
    game = Game.query.get(game_id)
    stocks = Stock.query.order_by(Stock.symbol).limit(25)

    #for stock in stocks:
    #    stock.update()

    if game:
        player = game.get_player(g.user)
        if player:
            return render_template('stocks.html', user = g.user, game = game, stocks = stocks, player = player)
        else:
            flash("You are not participating in that game.")
            return redirect("/games")

    flash("Invalid game session.")
    return redirect('/games')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    """ User registration form """

    if g.user:
        return redirect('/games')

    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = User.register(displayname = form.displayname.data, email = form.email.data, password = form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Good work buddy")
            login_user(user)

            return redirect('/')
        except IntegrityError:
            flash("There's already an account under that e-mail address!", 'danger')
            return render_template("register.html", form=form)

    return render_template("register.html", form=form)


@app.route('/games/<game_id>/start', methods=['POST'])
def start_game(game_id):
    """Starts a game. """
    game = Game.query.get_or_404(game_id)
    if game.host_id != g.user.id:
        flash("You are not the host of this game!")
        return redirect(f'/games/{game_id}')
    
    if game.start_game():
        flash("Game Start!")
        return redirect(f'/games/{game_id}')
    else:
        flash("The game has already ended. How are you even seeing this?")
        return redirect('/games')


#TODO shorten
@app.route('/api/stock/search', methods=['GET'])
def do_search():
    """Tries to find a stock in the local database, if not, we will search using the API."""
    term = request.args.get('term')

    if not term:
        return jsonify({
            'error': "Search term cannot be blank"
            })

    stock = Stock.query.get(term)

    if stock:
        return jsonify({
            'stocks': [stock.serialize()]
        })

    search = market.search(term)

    if not search:
        return jsonify({
            'error': "Invalid stock found."
            }), 405

    if search.get('error'):
        return jsonify({
            'error': search['error']
            }), 405
        
    ##TODO return multiple
    new_stocks = []

    for result in search['result']:
        symbol = result['symbol']
        if result['type'] != 'Common Stock':
            continue

        stock = Stock.query.get(symbol)
        stock_invalid = False
        if not stock:
            stock = Stock(symbol=symbol)
            stock.update()
            #workaround. remove invalid stocks
            if stock.current is None or stock.current < .05:
                stock_invalid = True

            if not stock_invalid:
                db.session.add(stock)
                new_stocks.append(stock)
        else:
            new_stocks.append(stock)

    db.session.commit()

    return jsonify({
        'stocks': [stock.serialize() for stock in new_stocks]
    })

@app.route('/api/games/<player_id>/history', methods=['GET'])
def get_game_history(player_id):
    """Given a game ID, get the game history"""
    history = PlayerHistory.query.filter(PlayerHistory.player_id == player_id).all()

    return jsonify({
        'history': [hist.serialize() for hist in history]
    }), 201


@app.route('/api/games/<game_id>/info', methods=['GET'])
def get_game_info(game_id):
    """Given a game ID, get the game information"""
    game = Game.query.get_or_404(game_id)
    game_dict = game.serialize()
    return jsonify(game_dict), 201

@app.route('/api/games/<game_id>/messages', methods=['GET'])
def get_game_messages(game_id):
    """Given a game ID, get the game messages"""
    messages = Message.query.filter(Message.game_id == game_id).order_by(Message.timestamp.desc()).limit(8)
    list_msg = [msg.serialize() for msg in messages]
    return jsonify(list_msg), 201


@app.route('/api/games/<game_id>/player', methods=['get'])
def get_player_stats(game_id):
    """Given a game ID, get the logged-in players stats for that game"""
    game = Game.query.get_or_404(game_id)
    player = game.get_player(g.user)
    player_dict = player.serialize()

    return jsonify(player_dict), 201

@app.route('/api/stock', methods=['GET'])
def get_stock():
    """Get the most up to date version of the stock. If we are rate limited, get the cached version."""
    symbol = request.args.get('symbol')
    stock = Stock.query.get_or_404(symbol)
    resp = stock.update()

    if not resp:
        return jsonify(stock.serialize()), 202
    
    return jsonify( stock.serialize() ) , 201

@app.route('/games/<game_id>/trade/sell', methods=['POST'])
def sell_stock(game_id):
    """Execute a trade"""
    game = Game.query.get_or_404(game_id)
    player = game.get_player(g.user)

    if not game.active:
        return jsonify({
            'error': "The game has not started yet."
        })

    #TODO workaround
    if player.user_id != g.user.id:
        return jsonify({
            'error': "You're not authorized to perform this transaction."
        })

    data = request.json
    stock_amt = float(data.get("stock"))
    symbol = data.get("symbol")
    stock = Stock.query.get(symbol)
    stock.update(True)

    owned_stock = PlayerStock.query.filter(PlayerStock.player_id == player.id, PlayerStock.symbol == symbol).first()

    if owned_stock.quantity < stock_amt:
        return jsonify({
            'error': 'You do not have enough shares to sell.'
        })

    owned_stock.quantity -= stock_amt
    cash_amt = stock_amt * stock.current

    owned_stock.money_spent -= cash_amt
    player.balance += cash_amt
    g.user.sells += 1
    g.user.trades += 1

    db.session.commit()
    game.add_message(player, f"{player.user.displayname} sold {stock_amt} shares of %s{owned_stock.symbol}% for {format_money(cash_amt)} at {format_money(stock.current)} each.")
    
    return jsonify({
        'response': f"You have successfully sold {stock_amt} shares of {owned_stock.symbol} for {format_money(cash_amt)}.",
        'player': player.serialize()
        })

@app.route('/games/<game_id>/trade/buy', methods=['POST'])
def buy_stock(game_id):
    """Execute a trade"""
    game = Game.query.get_or_404(game_id)
    player = game.get_player(g.user)
    data = request.json
    
    if not game.active:
        return jsonify({
            'error': "The game has not started yet."
        })

    #TODO workaround
    if player.user_id != g.user.id:
        return jsonify({
            'error': "You're not authorized to perform this transaction."
        })


    symbol = data.get("symbol")
    stock = Stock.query.get(symbol)
    stock.update(True)

    stock_amt = float(data.get("stock"))
    cash_amt = float(data.get("amount")) #Try not to spend more than 1% of the desired amount
    cash_amt = stock_amt * stock.current

    #print(f"Trying to execute purchase for {symbol}. Spending {cash_amt} for {stock_amt} stocks.")

    if cash_amt > player.balance:
        return jsonify({
            'error': 'You do not have the necessary funds.'
        })

    #get a stock owned by the player, if available
    owned_stock = PlayerStock.query.filter(PlayerStock.player_id == player.id, PlayerStock.symbol == symbol).first()
    if not owned_stock:
        owned_stock = PlayerStock(player_id = player.id, symbol = symbol)
        owned_stock.quantity = 0
        owned_stock.money_spent = 0
        db.session.add(owned_stock)

    owned_stock.quantity += stock_amt
    owned_stock.money_spent += cash_amt
    player.balance -= cash_amt
    g.user.buys += 1
    g.user.trades += 1

    db.session.commit()
    game.add_message(player, f'{player.user.displayname} purchased {stock_amt} shares of %s{owned_stock.symbol}% for {format_money(cash_amt)} at {stock.current} each.')

    return jsonify({
        'response': f"You have successfully purchased {stock_amt} shares of {owned_stock.symbol} for {format_money(cash_amt)}.",
        'player': player.serialize()
        })

@app.route('/logout', methods=['POST'])
def logout():
    """ Deletes the user from the session """
    g.user = None
    del session[CURR_USER_KEY]
    flash("Successfully logged out")
    return redirect('/')

def login_user(user):
    """ Saves the user to the session """
    session[CURR_USER_KEY] = user.id

#TODO user profiles don't work
#TODO change the color of the modal to better fit the scheme
#TODO add graphing using chart.js and the historical data we've saved
#TODO purge old games from the database and older historical data as not to make our db too bloated
#TODO add images for people to look at