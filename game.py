import threading
import os
import datetime
from models import User, connect_db, db, Game, Player, Stock, PlayerStock, Message

def main():
    """Main logic loop. Runs every second."""
    #Check all games to see if any of them have ended.
    games = Game.query.all()
    for game in games:
        if datetime.now() > game.end_date:
            print(f'Game {game.id} needs to end.')
            game.end()


main_timer = threading.timer(10, main)
main_timer.start()
