# Stocks Game

Based on live stock market data, players you can manage virtual portfolios in a competitive environment with their friends!

Live at [stocks game](https://stocks-game.herokuapp.com/).

## Introduction

Through this app, players can set up game sessions and browse and purchase stocks using real-life data. Games can last anywhere from a minute to a week, and are affected by real life stock fluctuations.

Aside from the competitive element, this game provides the user with a risk free way of practicing and learning about the stock market.

## Getting Started

1. Register for an account.

2. Go to the *Games* section on the navbar to browse games.

3. Here, you can either join a game or create a new one.

4. Invite friends to play your game.

5. Start the game and begin trading! Keep a close eye on stock market trends and financial news.


## APIs Used

This application was built on Flask with a Postgres back-end for database. The front-end was built on Bootstrap for visuals and site responsiveness. Our realtime stock market data is pulled using [finnhub.io](https://finnhub.io).

## Schema

Through our API, we make frequent requests to the stock market for current stock prices and score the players based on how their returns are. To this end, we use various PSQL tables to store this information.

A diagram of the schema can be seen [here](https://raw.githubusercontent.com/erojas4704/stocks-game/master/Schema.png).


## Features

- **Player Listings**
    Allows players to see the standing and balance of all other players in the game session. Included to allow for the competitive element of the game to shine through.

- **Search**
    Allows users to search for stocks within our database, if it doesn't exist, the API will find it and add it. This was incorporated to allow players to buy stocks they are familiar with, even if they don't exist in our database.

- **Execute stock trades**
    Allows users to buy and sell stocks with their virtual portfolio. The data is validated every step of the way, so users are unable to cheat. This is the whole point of the game and without there'd be no virutal portfolio.

- **History Messages**
    Allows users to see the latest sales and purchases their opponents have made. 

- **Live Updates**
    The game states are rendered live on screen so users can keep track of the game without constantly refreshing.


## Upcoming Changes

1. Make functional user profiles using our user metrics we've saved. 
2. Change the color of the modal to better fit the scheme.
3. Add graphing using chart.js and the historical data we've saved.
4. Purge old games from the database and older historical data as not to make our database too bloated.
5. Add stock images to spruce up the design.
6. Add company descriptions and news stories.
7. Allow users to view the full portfolio of all other users.
8. Private game functionality.
9. Allow games to have their own rules for day-trading or fractional shares.
10. Leaderboards.
11. Crypto integration.

