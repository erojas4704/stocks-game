"""Models """

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_bcrypt import Bcrypt
from datetime import date, timedelta, datetime
from secrets import STOCK_UPDATE_LIMIT_MINUTES
import market

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

        if self.name is None:
            basic = market.basic_details(self.symbol.upper())

            if basic:
                self.name = basic["name"]

        if resp:
            self.current = resp['c']
            self.open = resp['o']
            self.close = resp['pc']
            self.high = resp['h']
            self.low = resp['l']

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


class Player(db.Model):
    """The model for the users in games. 
    This will record all game statistics for that user and game, as well."""
    __tablename__ = 'players'

    id = db.Column(
        db.Integer,
        unique = True,
        primary_key = True,
        autoincrement=True
    )

    user = relationship("User")

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
        default = 0
    )

    color = db.Column(
        db.Integer
    )

    stocks = db.relationship(
        "PlayerStock"
    )

    def get_total_worth(self):
        """Calculate the value of all owned stocks + balance"""
        port = self.get_portfolio_value()

        return port + self.balance


    def get_portfolio_value(self):
        """Calculate the value of all owned stocks"""
        value = 0
        for stock in self.stocks:
            value += stock.quantity * stock.stock.current

        return value


    def serialize(self):
        """Return a dictionary describing this object."""
        return {
            "id": self.id,
            "gameID": self.game_id,
            "userID": self.user_id,
            "balance": self.balance,
            "color": self.color,
            "portfolio": self.get_portfolio_value(),
            "stocks": [stock.serialize() for stock in self.stocks]
        }

    def __repr__(self):
        return f"<{self.user.displayname}: {self.balance}>"

class Game(db.Model):
    """The model for the Game"""
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    starting_balance = db.Column(db.Float, nullable=False)
    max_players = db.Column(db.Integer, nullable=False)
    fractional_shares = db.Column(db.Boolean)
    password = db.Column(db.Text)
    minutes = db.Column(db.Float, nullable=False)
    hours = db.Column(db.Float, nullable=False)
    days = db.Column(db.Float, nullable=False)

    host_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id')
    )

    players = relationship(
        "Player"
    )

    users = relationship(
        "User",
        secondary="players"
    )

    allow_off_market_trades = db.Column(
        db.Boolean,
        default = False
    )

    duration = None
    active = db.Column(
        db.Boolean,
        default = False,
        nullable = False
    )

    def serialize(self):
        """JSON Friendly Dict"""
        return {
            "active": self.active,
            "players": [player.serialize() for player in self.players],
            "start": self.start,
            "end": self.end,
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

    def start_game(self):
        """Starts the game. Calculates the end time"""
        duration = timedelta(
            days = self.days,
            minutes = self.minutes,
            hours = self.hours
        )

        self.start = datetime.now()
        self.end = self.start + duration
        self.active = True

        db.session.commit()

    @classmethod
    def generate_game(cls):
        """Given a duration, creates a game and automatically sets the start time to be now and end time to be start time + the duration."""
        return Game()
    



class User(db.Model):
    """The model for the User"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    displayname = db.Column(db.Text, nullable=False, unique=True)

    avatar_url = db.Column(
        db.Text
    )
    
    games = db.relationship(
        "Game",
        secondary="players",
        primaryjoin=(Player.user_id == id),
    )



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
        print("OK ")
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False

    def __repr__(self):
        return f"<User #{self.email}: {self.displayname}>"

