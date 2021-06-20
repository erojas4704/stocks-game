"""Game tests"""
# run these tests like:
#
# python -m unittest test_games.py

import os
from unittest import TestCase
from dotenv import load_dotenv
os.environ['DB_URL'] = "postgresql://ass:ass@localhost:5432/stocksgame_test"
load_dotenv()

from models import db, Game, User, Player, Message
from secrets import DB_USER, DB_PASSWORD

from app import app
import game

db.create_all()


class GameTestCase(TestCase):
    def setUp(self):
        Message.query.delete()
        Game.query.delete()
        Player.query.delete()
        User.query.delete()

        self.users = []
        self.client = app.test_client()
        self.users.append(
            User.register(
                email="kenton_porner@gmail.com",
                displayname="Kenton",
                password="123456"
            )
        )
        self.users.append(
            User.register(
                email="donaldtrump@gmail.com",
                displayname="Donald J Trump",
                password="123456"
            )
        )
        self.users.append(
            User.register(
                email="elputotulio@gmail.com",
                displayname="Tulio",
                password="123456"
            )
        )
        self.users.append(
            User.register(
                email="captainamerica@gmail.com",
                displayname="Sexhaverirl",
                password="123456"
            )
        )
        self.users.append(
            User.register(
                email="lord_of_thunder@gmail.com",
                displayname="Cuntwrecker6000",
                password="123456"
            )
        )

        for user in self.users:
            db.session.add(user)

        db.session.commit()

        self.testgame = Game(
            starting_balance=1000,
            max_players=20,
            minutes=1,
            hours=0,
            days=0
        )

        db.session.add(self.testgame)
        db.session.commit()

        for user in self.users:
            self.testgame.add_player(user)

        db.session.commit()
    
    def tearDown(self):
        print('thanks')

    def test_winner(self):
        """Does the game determine the right winner?"""
        i = len(self.testgame.players)
        for player in self.testgame.players:
            i += 1
            player.balance = 0 + i * 10
        
        self.testgame.players[3].balance = 500
        
        self.testgame.end_game()
        winner_user = self.testgame.players[3].user
        winner_id = self.testgame.winner_id

        self.assertEqual(winner_user.id, winner_id)

    game.active = False