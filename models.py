"""Models """

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_bcrypt import Bcrypt
from datetime import timedelta, datetime
from operator import attrgetter
import market
import utils
import os

STOCK_UPDATE_LIMIT_MINUTES = float(os.environ.get("STOCK_UPDATE_LIMIT_MINUTES"))

db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    """Connect to Database"""
    db.app = app
    db.init_app(app)
    db.create_all()


class Stock(db.Model):
    """The model for stocks"""
    __tablename__ = 'stocks'
    symbol = db.Column(
        db.Text,
        primary_key = True,
        unique=True,
        nullable = False
    )

    name = db.Column(
        db.Text
    )

    open = db.Column(
        db.Float,
        default = 0
    )

    close = db.Column(
        db.Float,
        default = 0
    )

    current = db.Column(
        db.Float,
        default = 0
    )

    high = db.Column(
        db.Float,
        default = 0
    )

    low = db.Column(
        db.Float,
        default = 0
    )

    last_updated = db.Column(
        db.DateTime
    )

    def serialize(self):
        """Return a dictionary serialized verion of the stock"""
        stock_dict = {
            "symbol": self.symbol,
            "name": self.name,
            "open": self.open,
            "close": self.close,
            "current": self.current,
            "high": self.high,
            "low": self.low,
            "last_updated": self.last_updated
        }
        return stock_dict

    def update(self, force = False):
        """Update a stock from the remote API. TODO Only if the stock hasn't been updated in the last 5 min. """

        if self.last_updated is None or force:
            minutes = 9999
        else:
            time_difference = datetime.now() - self.last_updated
            minutes = time_difference.total_seconds()/60

        if minutes < STOCK_UPDATE_LIMIT_MINUTES:
            return False
        
        self.last_updated = datetime.now()
            
        resp = market.quote(self.symbol.upper())

        if resp.get('error'):
            print(resp['error'])
            print(f'[CRITICAL]: Could not get any information for {self.symbol}.')
            return

        if self.name is None:
            basic = market.basic_details(self.symbol.upper())

            if basic:
                self.name = basic["name"]

        if resp:
            print(f'{resp} {self.symbol}')
            self.current = resp['c']
            self.open = resp['o']
            self.close = resp['pc']
            self.high = resp['h']
            self.low = resp['l']
        
        history = StockHistory(
            symbol = self.symbol,
            timestamp = datetime.now(),
            price = self.current
        )

        db.session.add(history)
        db.session.commit()
        return resp


class PlayerStock(db.Model):
    """The model for a player's stocks"""
    __tablename__ = 'playerstocks'

    player_id = db.Column(
        db.Integer,
        db.ForeignKey('players.id', ondelete="cascade"),
        primary_key=True,
    )

    symbol = db.Column(
        db.Text,
        db.ForeignKey('stocks.symbol', ondelete="cascade"),
        primary_key=True
    )

    quantity = db.Column(
        db.Integer,
        nullable=False,
        default = 0
    )

    money_spent = db.Column(
        db.Float,
        nullable=False,
        default = 0
    )

    stock = relationship("Stock")
    
    def serialize(self):
        """Make it JSON friendly"""
        return {
            'symbol': self.symbol,
            'quantity': self.quantity,
            'money_spent': self.money_spent
        }


class PlayerHistory(db.Model):
    """Will keep track of fluctuating player balances throughout games."""
    __tablename__ = 'playerhistory'

    id = db.Column(
        db.Integer,
        unique=True,
        primary_key=True,
        autoincrement=True
    )

    player_id = db.Column(
        db.Integer,
        db.ForeignKey('players.id', ondelete="cascade"),
        primary_key=True,
    )

    value = db.Column(
        db.Float,
        default=0
    )

    timestamp = db.Column(
        db.DateTime,
        default=datetime.now(),
        nullable=False
    )


    @classmethod
    def record(cls, player, amount):
        hist = PlayerHistory(
            player_id=player.id,
            value=amount
        )

        histories = PlayerHistory.query.filter(PlayerHistory.player_id == player.id).order_by(PlayerHistory.timestamp.desc()).limit(1)
        if(histories)
            last = histories[0]

        if last and last.timestamp == hist.timestamp:
            return False

        #TODO don't save identical histories
        db.session.add(hist)
        db.session.commit()

    def serialize(self):
        """Make it JSON friendly"""
        return {
            'playerID': self.player_id,
            'balance': self.value,
            'timestamp': self.timestamp
        }


class Player(db.Model):
    """The model for the users in games.
    This will record all game statistics for that user and game, as well."""
    __tablename__ = 'players'

    id = db.Column(
        db.Integer,
        unique=True,
        primary_key=True,
        autoincrement=True
    )

    user = relationship(    
        "User"
    )
    
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    game_id = db.Column(
        db.Integer,
        db.ForeignKey('games.id', ondelete="cascade"),
        primary_key=True,
    )

    balance = db.Column(
        db.Float,
        default=0
    )

    color = db.Column(
        db.Integer
    )

    stocks = db.relationship(
        "PlayerStock"
    )

    final_value = db.Column(
        db.Float,
        default=0
    )

    final_standing = db.Column(
        db.Integer
    )

    def get_total_worth(self):
        """Calculate the value of all owned stocks + balance"""
        port = self.get_portfolio_value()

        total = port + self.balance
        #log the value to history
        PlayerHistory.record(self, total)


        return port + self.balance

    def get_portfolio_value(self):
        """Calculate the value of all owned stocks"""
        value = 0
        for stock in self.stocks:
            value += stock.quantity * stock.stock.current

        return value

    def get_return(self):
        """Calculate the money gained from stocks."""
        value = 0
        spent = 0
        for stock in self.stocks:
            value += stock.quantity * stock.stock.current
            spent += stock.money_spent
        
        return value - spent

    def serialize(self):
        """Return a dictionary describing this object."""
        return {
            "id": self.id,
            "gameID": self.game_id,
            "userID": self.user_id,
            "balance": self.balance,
            "color": self.color,
            "returns": self.get_return(),
            "portfolio": self.get_portfolio_value(),
            "user": self.user.serialize(),
            "stocks": [stock.serialize() for stock in self.stocks]
        }

    def __repr__(self):
        return f"<{self.user.displayname}: {self.balance}>"


class Message(db.Model):
    """Message for user activity or chat"""
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    player = db.relationship("Player")

    player_id = db.Column(
        db.Integer,
        db.ForeignKey('players.id', ondelete="cascade")
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    game_id = db.Column(
        db.Integer,
        db.ForeignKey('games.id', ondelete="cascade")
    )

    timestamp = db.Column(db.DateTime, default=datetime.now())

    def serialize(self):
        """JSON Friendly Dict"""
        return {
            'timestamp': self.timestamp,
            'message': self.message
        }


class Game(db.Model):
    """The model for the Game"""
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.Text) #TODO limit size
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    starting_balance = db.Column(db.Float, nullable=False)
    max_players = db.Column(db.Integer, nullable=False) #TODO not yet implemented
    fractional_shares = db.Column(db.Boolean) #TODO not yet implemented
    allow_off_market = db.Column(db.Boolean) #TODO not yet implemented
    password = db.Column(db.Text)#TODO not yet implemented
    minutes = db.Column(db.Float, nullable=False)
    hours = db.Column(db.Float, nullable=False)
    days = db.Column(db.Float, nullable=False)
    
    host_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id')
    )

    players = relationship(
        "Player",
        cascade="all, delete"
    )

    users = relationship(
        "User",
        secondary="players",
        cascade="all, delete"
    )

    allow_off_market_trades = db.Column(
        db.Boolean,
        default = False
    )

    winner_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade")
    )

    duration = None
    active = db.Column(
        db.Boolean,
        default = False,
        nullable = False
    )

    def serialize(self):
        """JSON Friendly Dict"""
        players = self.players
        players.sort(key=utils.total_sort, reverse=True)

        return {
            "active": self.active,
            "players": [player.serialize() for player in players],
            "start": self.start.isoformat() if self.start else None,
            "winner_id": self.winner_id,
            "end": self.end.isoformat() if self.end else None,
            "id": self.id
        }

    def get_player(self, user):
        """Get the game's player reference from a global user"""
        if not user:
            return None

        player = Player.query.filter(Player.user_id == user.id, Player.game_id == self.id).first()

        if player and user.id != player.user_id:
            return None
            
        return player

    def add_message(self, player, message):
        message = Message(player_id = player.id,
            game_id = self.id,
            message = message
        )
        db.session.add(message)
        db.session.commit()

    def add_player(self, user, password = None):
        """Add player to the game if a player isn't already in the game and the password is correct"""
        if self.password is None or password == self.password:
            if user not in self.players:
                self.users.append(user)
                player = self.get_player(user)
                player.balance = self.starting_balance
                db.session.commit()
                return True
        
        return False

    def get_remaining_time(self):
        """Returns how much time is left, in seconds"""
        return (self.end - datetime.now()).total_seconds()

    def start_game(self):
        """Starts the game. Calculates the end time"""
        
        if self.end is not None:
            return False

        duration = timedelta(
            days=self.days,
            minutes=self.minutes,
            hours=self.hours
        )

        self.start = datetime.now()
        self.end = self.start + duration
        self.active = True
        self.add_message(self.players[0], "The game has been started")

        db.session.commit()
        return True
    
    def end_game(self):
        """Ends the game and declares a winner"""
        self.active = False
        for player in self.players:
            player.final_value = player.get_total_worth()
            player.user.played += 1
            player.user.total_return += player.get_return()
    
        players = self.players
        players.sort(key=attrgetter("final_value"), reverse=True)
        players[0].user.wins += 1

        self.winner_id = players[0].user.id
        db.session.commit()
        print(f"Game overed quickly. The winner is {players[0].user.displayname}")
        self.add_message(players[0], f"The game is now over. The winner is {players[0].user.displayname}")

    @classmethod
    def generate_game(cls):
        """Given a duration, creates a game and automatically sets the start time to be now and end time to be start time + the duration."""
        return Game()
    
class StockHistory(db.Model):
    """History of stock prices"""

    __tablename__ = 'stockhistory'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    symbol = db.Column(
        db.Text,
        nullable = False
    )

    price = db.Column(
        db.Float,
        default=0,
        nullable=False
    )

    timestamp = db.Column(
        db.DateTime, 
        default=datetime.now(),
        nullable=False
    )
    
    def serialize(self):
        """Make it JSON friendly"""
        return {
            'playerID': self.player_id,
            'balance': self.balance,
            'timestamp': self.timestamp
        }


class User(db.Model):
    """The model for the User"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    displayname = db.Column(db.Text, nullable=False, unique=True)

    wins = db.Column(db.Integer, default=0)
    played = db.Column(db.Integer, default=0)
    total_return = db.Column(db.Float, default=0)
    trades = db.Column(db.Integer, default=0)
    buys = db.Column(db.Integer, default=0)
    sells = db.Column(db.Integer, default=0)

    avatar_url = db.Column(
        db.Text
    )
    
    games = db.relationship(
        "Game",
        secondary="players",
        primaryjoin=(Player.user_id == id),
    )

    def serialize(self):
        """Return JSON friendly"""
        return {
            'id': self.id,
            'displayname': self.displayname
        }


    @classmethod
    def register(cls, email, displayname, password):
        """static method for user registration. Returns the instance of the user registered."""
        hashed_pw = bcrypt.generate_password_hash(password = password)
        buffer_pw = hashed_pw.decode('utf-8')

        return User(
            displayname = displayname,
            password = buffer_pw,
            email = email)
            
    @classmethod
    def authenticate(cls, email, password):
        """Authenticates user using Bcrypt"""
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False

    def __repr__(self):
        return f"<User #{self.email}: {self.displayname}>"

