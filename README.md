# Team-finder-telegram-bot
The __Team Finder Telegram Bot__ helps users find teammates for different games.
It is powered by [Redis](https://redis.io/)  and [MongoDB](https://www.mongodb.com/) 

## Technoogies
  - [Redis](https://redis.io/): Used as temporary storage for quick data access.
  - [MongoDB](https://www.mongodb.com/): Serves as the primary database for storing user data.
  - [Python-telegram-bot](https://python-telegram-bot.org/): The main library for interacting with the Telegram API.

## Brief overview
### Data collection
1. The bot collects user data, which is then saved to __MongoDB__

![image](https://github.com/user-attachments/assets/df4bf28e-3361-4fcb-9a5e-bd2bba8f89a1)

### User options
2. After data collection, the user has two options:  
   - Create a team  
   - search for a team to join

### Joining a Team
4. If the user chooses to join a team, he simply uses the __/find__ command. The bot then tries to find the best match based on the data provided by the user.
![image](https://github.com/user-attachments/assets/d4dd9722-d2bb-493f-9403-989ff1f4a6cb)

### Creating a Team
5. If the user chooses to create a team, they provide the necessary information to the bot.
The bot stores this data in __Redis__, which saves and indexes it for a certain time
(15 minutes by default). During this period, other users can join the team.

![image](https://github.com/user-attachments/assets/191918f3-2616-462a-b099-ee5564a08d15)

## Structure
```
.
├── data
│   └── mongodb
├── docker-compose.yaml
├── Dockerfile
├── games.json
├── LICENSE
├── main.py
├── Makefile
├── poetry.lock
├── pyproject.toml
├── README.md
├── src
│   ├── bot
│   │   ├── constants.py
│   │   ├── filters.py
│   │   ├── handlers
│   │   │   ├── base.py
│   │   │   ├── commands.py
│   │   │   ├── conversations.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   └── utils
│   │       ├── __init__.py
│   │       └── parsers.py
│   ├── common
│   │   ├── config.py
│   │   ├── di.py
│   │   ├── filters.py
│   │   ├── __init__.py
│   │   └── utils.py
│   ├── domain
│   │   ├── entities
│   │   │   ├── games
│   │   │   │   ├── base.py
│   │   │   │   ├── impl.py
│   │   │   │   └── __init__.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── infra
│   │   ├── __init__.py
│   │   └── repositories
│   │       ├── base.py
│   │       ├── impl.py
│   │       └── __init__.py
│   └── __init__.py
└── tests
    ├── conftest.py
    ├── details
    │   ├── conftest.py
    │   ├── __init__.py
    │   ├── test_mongo_repo.py
    │   └── test_redis_repo.py
    ├── domain
    │   ├── entities
    │   │   ├── conftest.py
    │   │   ├── __init__.py
    │   │   ├── test_games.py
    │   │   ├── test_groups.py
    │   │   └── test_user.py
    │   └── __init__.py
    └── __init__.py
```
