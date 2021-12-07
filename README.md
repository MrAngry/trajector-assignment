# Introduction
 Trajector assignment 

## Main libraries used
 - FastAPI 
 - TortoiseORM - (this was an unfortunate choice )
 - pytest
 - requests 

## How to run project
- run `./scripts/build.sh`

### Documentation
- run `./scripts/build.sh`
- open `localhost:9080/docs`

#### Ports
- fastapi backend available at `localhost:9080`
- postgreSQL `localhost:5432`


### Run tests with coverage
run `./scripts/test-local.sh`

## Project structure
```
.
├── README.md
├── app
│   ├── Dockerfile
│   ├── __init__.py
│   ├── api
│   │   ├── __init__.py
│   │   └── api_v1
│   │       ├── __init__.py
│   │       ├── api.py
│   │       └── endpoints
│   │           ├── __init__.py
│   │           ├── items.py
│   │           └── tags.py
│   ├── config.py
│   ├── main.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── doubly_linked_list.py
│   │   ├── item.py
│   │   └── tag.py
│   ├── requirements-dev.txt
│   ├── requirements.txt
│   ├── schemas
│   │   ├── __init__.py
│   │   └── item.py
│   ├── scripts
│   │   └── test.sh
│   ├── static
│   │   └── user_uploads
│   └── tests
│       ├── __init__.py
│       ├── conftest.py
│       └── test_double_linked_list.py
├── docker-compose.override-test.yml
├── docker-compose.override.yml
├── docker-compose.yml
└── scripts
    ├── build.sh
    └── test-local.sh
```

## Bonus objective taken
- filter by tags or is_favorite
- asynchronous thumbnail download
- customizable settings for download retires and timeouts

### Side note

During development of this assignment a bug was found in the ORM system used to develop solution this hindered
progress extremely https://github.com/tortoise/tortoise-orm/issues/1002