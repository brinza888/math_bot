# Math bot
Copyright (C) 2021 Ilya Bezrukov, Stepan Chizhov, Artem Grishin

Licensed under GNU GPL-2.0-or-later

Working telegram bot from this repository you can find here:
- [@linal_angem_bot](https://t.me/linal_angem_bot)

## Features
Bot for Telegram that help you to solve some math problems. Now it can solve:
- Find determinant of square matrix (max size is 8x8) (/det)
- Build truth table for any logic expression (/logic)
- Find GCD and solve Diofant linear equation (/gcd)
- Find factorization for number (/factorize)
- Find modular inverse (/inverse)
- Find idempotent elements in Z/n ring (/idempotents)
- Find nilpotent elements in Z/n ring (/nilpotents)

## Installation
1. Create bot account in telegram using @BotFather, get API token.
2. Clone this repository to your server or computer
3. Create file .env in project root
4. Write yor configuration in .env file
5. Be sure, that you have passed bot token in BOT_TOKEN config variable in .env
6. Install all python3 libraries specified in requirements.txt
7. Run tg.py file:
   > python3 tg.py
  
   Or:
   
   > python tg.py

## Configuration

### Main configuration
- DATABASE_URI
  - URI (or path) to database, where bot will save logs.
  - Type: str
  - Default: "sqlite:///bot.db"
- DEBUG
  - Enable debug mode. In **production** be sure, that DEBUG = 0!
  - Type: 0 or 1
  - Default: 0
- BOT_TOKEN
  - API token for telegram bot (You can get it from @BotFather).
  - Type: str
  - **Required**

### Calculation limits
- MAX_MATRIX
  - /det limit
  - Type: int
  - Default: 8
- MAX_VARS
  - /logic limit
  - Type: int
  - Default: 7
- MAX_MODULO
  - Maximum ring modulo (Z/n)
  - Type: int
  - Default: 10 ^ 15
- MAX_ELEMENTS
  - Maximum elements to list in message
  - Type: int
  - Default: 101
- FACTORIZE_MAX
  - /factorize limit
  - Type: int
  - Default: 10 ^ 12

## Running in background forever
Use systemd units or Docker containers.
