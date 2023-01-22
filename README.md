# Math bot
Copyright (C) 2021-2023 Ilya Bezrukov, Stepan Chizhov, Artem Grishin\
Licensed under GNU GPL-2.0-or-later

Currently maintained by:
- [Ilya Bezrukov](https://github.com/BrinzaBezrukoff)
- [Stepan Chizhov](https://github.com/Teh1Z)

Working telegram bot from this repository you can find here:
- [@linal_angem_bot](https://t.me/linal_angem_bot)

# Features
Bot for Telegram that help you to solve some math problems.
## /logic
Construct truth table for logic expression.\
Supported operators:

|  char  	|     name    	| priority 	|
|:------:	|:-----------:	|:--------:	|
|    ~   	|     NOT     	|    20    	|
|    &   	|     AND     	|    10    	|
| &#124; 	|      OR     	|     5    	|
|    ^   	|     XOR     	|     5    	|
|    >   	| implication 	|     2    	|
|    =   	| equivalence 	|     2    	|

Supported constant values:

| designation |  description  |
|:-----------:|:-------------:|
|      1      | logical True  |
|      0      | logical False |

## /calc
Calculate (evaluate) given mathematical expression.
#### Supported operators
| char 	|         name        	| priority 	| associativity 	|
|:----:	|:-------------------:	|:--------:	|:-------------:	|
|   +  	|       addition      	|     1    	|      left     	|
|   -  	|     subtraction     	|     1    	|      left     	|
|   *  	|    multiplication   	|     2    	|      left     	|
|   /  	|       division      	|     2    	|      left     	|
|   :  	|    floor division   	|     2    	|      left     	|
|   %  	|        modulo       	|     2    	|      left     	|
|   -  	|       negative      	|     5    	|      left     	|
|   +  	|       positive      	|     5    	|      left     	|
|   ^  	|         power       	|    10    	|   **right**   	|

#### Supported functions
|     Name     	|            Description           	|  Aliases  	|
|:------------:	|:--------------------------------:	|:---------:	|
|              	|          **GENERAL USE**         	|           	|
|    abs(x)    	|       Absolute value of _x_      	|           	|
|   round(x)   	|          Round float _x_         	|           	|
|   pow(x, p)  	|         Power _x_ in _p_         	|           	|
|    sqrt(x)   	|       Square root from _x_       	|           	|
| factorial(x) 	|         Factorial of _x_         	|           	|
|              	|      **ANGULAR CONVERSION**      	|           	|
|    deg(x)    	|     Degrees from _x_ radians     	|           	|
|    rad(x)    	|     Radians from _x_ degrees     	|           	|
|              	|         **TRIGONOMETRIC**        	|           	|
|    sin(x)    	|               sinus              	|           	|
|    cos(x)    	|              cosine              	|           	|
|    tan(x)    	|              tangent             	|   tg(X)   	|
|    cot(x)    	|             cotangent            	|   ctg(x)  	|
|    acos(x)   	|            arc-cosine            	| arccos(x) 	|
|    asin(x)   	|             arc-sine             	| arcsin(x) 	|
|    atan(x)   	|            arc-tangent           	|  arctg(x) 	|
|              	|          **LOGARITHMS**          	|           	|
|   log(x, b)  	| Logarithm from _x_ with base _b_ 	|           	|
|     lg(x)    	| Logarithm from _x_ with base 10  	|           	|
|     ln(x)    	| Logarithm from _x_ with base _e_ 	|           	|
|    log2(x)   	|  Logarithm from _x_ with base 2  	|           	|
|    exp(x)    	|         Power _e_ in _x_         	|           	|

#### Supported pre-defined constants
| Designation 	|      Description     	|      Value      	|
|:-----------:	|:--------------------:	|:---------------:	|
|      e      	|  Value of _e_ number 	|  Python: math.e 	|
|      pi     	| Value of _pi_ number 	| Python: math.pi 	|



# Developers information
## Installation
1. Create bot account in telegram using @BotFather, get API token.
2. Clone this repository to your server or computer
3. **Create file .env in project root**
4. Write yor configuration in .env file
5. Be sure, that you have passed bot token in BOT_TOKEN config variable in .env
6. Install all python3 libraries specified in requirements.txt
7. Run tg.py file:
   > python3 tg.py
  
   Or (depends on python installation):
   
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
- ADMINS
  - List of admin IDs (separated by any whitespace character)
  - Type: str

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
- CALC_LINE_LIMIT
- CALC_OPERAND_LIMIT
- CALC_POW_UNION_LIMIT
- CALC_POW_EACH_LIMIT
- CALC_FACTORIAL_LIMIT

### Additional configuration
- GITHUB_LINK
- CHANNEL_LINK
