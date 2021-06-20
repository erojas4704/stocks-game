import threading
import os
import random
import time
from datetime import timedelta, datetime
from models import User, connect_db, db, Game, Player, Stock, PlayerStock, Message

active = True

def main():
    """Main logic loop. Runs every 10 seconds."""
    #Check all games to see if any of them have ended.
    games = Game.query.filter(Game.active==True).all()
    #print(f'CHECKING AL GAMES {games}')
    for game in games:
        #players = Player.query.filter(Player.game_id == game.id).all()
        #for player in players:
        #    player.balance = random.uniform(0, 55000)
        #    db.session.commit()

        if datetime.now() > game.end:
            print(f'Game {game.id} needs to end.')
            game.end_game()


def main_wrapper():
    while active:
        main()
        time.sleep(10)

main_thread = threading.Timer(10, main_wrapper)
main_thread.start()
