from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_bcrypt import Bcrypt
from datetime import date, timedelta
from models import db, User, Stock
from sqlalchemy.exc import IntegrityError
import app

db.drop_all()
db.create_all()

try: 
    db.session.add(
        User.register("kenton_porner@gmail.com", "Kenton", "123456")
    )
    db.session.add(
        User.register("elputotulio@gmail.com", "Tulio Elputo", "123456")
    )
    db.session.add(
        User.register("donamaria@gmail.com", "Doña Maria", "123456")
    )
except IntegrityError:
    print("User already exists")

db.session.add(Stock(symbol="A"))
db.session.add(Stock(symbol="AAPL"))
db.session.add(Stock(symbol="ABNB"))
db.session.add(Stock(symbol="AMC"))
db.session.add(Stock(symbol="AMD"))
db.session.add(Stock(symbol="AMZN"))
db.session.add(Stock(symbol="BA"))
db.session.add(Stock(symbol="BB"))
db.session.add(Stock(symbol="BYND"))
db.session.add(Stock(symbol="C"))
db.session.add(Stock(symbol="COIN"))
db.session.add(Stock(symbol="CSCO"))
db.session.add(Stock(symbol="COST"))
db.session.add(Stock(symbol="CVX"))
db.session.add(Stock(symbol="D"))
db.session.add(Stock(symbol="DIS"))
db.session.add(Stock(symbol="FB"))
db.session.add(Stock(symbol="GME"))
db.session.add(Stock(symbol="GE"))
db.session.add(Stock(symbol="GOOGL"))
db.session.add(Stock(symbol="NVDA"))
db.session.commit()