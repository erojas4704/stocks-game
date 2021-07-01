"""Game tests"""
# run these tests like:
#
# python -m unittest test_games.py

import os
import json
from unittest import TestCase
from flask import g
from dotenv import load_dotenv

load_dotenv()
os.environ['DB_URL'] = os.environ.get('TEST_URL')



from models import db, Game, User, Player, Message

from app import app
from app import CURR_USER_KEY
import game

db.create_all()


class GameTestCase(TestCase):
    def setUp(self):
        Message.query.delete()
        Game.query.delete()
        Player.query.delete()
        User.query.delete()
        db.session.commit()

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

        db.session.commit()

        self.testgame = Game(
            starting_balance=1000,
            max_players=20,
            minutes=1,
            hours=0,
            days=0
        )
        
        for user in self.users:
            db.session.add(user)

        db.session.add(self.testgame)
        db.session.commit()

        for user in self.users:
            self.testgame.add_player(user)

        db.session.commit()
        
        self.testuser = self.users[0]
        #login my user
        with app.test_client() as client:
            client.post('/login', data = {
                'email': self.testuser.email,
                'password': '123456'
            });

    
    def tearDown(self):
        return

    def test_winner(self):
        """Does the game determine the right winner?"""
        return
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

    def test_purchasing(self):
        """Can an user execute trades without incident?"""
        
        self.testgame.start_game()
        with app.test_client() as client:
            response = client.post(f"/games/{self.testgame.id}/trade/buy")
        

        data_dict = json.loads(response.data)
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn("error", data_dict) 
