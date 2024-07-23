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

![image](https://github.com/user-attachments/assets/6afa3db0-6a6d-4317-9ca1-24e4375db895)

### User options
2. After data collection, the user has two options:  
   - Create a team  
   - search for a team to join

### Joining a Team
4. If the user chooses to join a team, he simply uses the __/find__ command. The bot then tries to find the best match based on the data provided by the user.
![image](https://github.com/user-attachments/assets/06b40dbc-ef7f-439d-b126-6201a39a564a)

### Creating a Team
5. If the user chooses to create a team, they provide the necessary information to the bot.
The bot stores this data in __Redis__, which saves and indexes it for a certain time
(15 minutes by default). During this period, other users can join the team.

![image](https://github.com/user-attachments/assets/d79219a9-b502-469a-b218-d778bfb8f631)

## Structure
```
.
├── data
├── docker-compose.yaml
├── Dockerfile
├── LICENSE
├── main.py
├── Makefile
├── plan.md
├── poetry.lock
├── pyproject.toml
├── README.md
├── src
│   ├── bot
│   │   ├── constants.py
│   │   ├── filters.py
│   │   ├── handlers
│   │   │   ├── base.py
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
│   │   │   ├── games.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── infra
│   │   ├── __init__.py
│   │   └── repositories
│   │       ├── base.py
│   │       ├── impl.py
│   │       └── __init__.py
│   └── __init__.py
├── test.py
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
