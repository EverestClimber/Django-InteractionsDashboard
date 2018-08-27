# 😷 Otsuka Insights

Link fileds from `docs/` like this: [API Docs](docs/api.md).

## Dependencies

* Python 3.5+
* PostgreSQL 9.6+

## Product deployment procedure

`TODO: write this!`

## Code Style guide

### Python

* PEP8
* relax line length restriction to max of 120
* Google Python Style Guide for comments **only** (it's easier to read than RST and closer to the Django/DRF style anyway)

## Dev environment setup

Postgres DB setup:

```
create user otskinter with password '...';
create database otskinter;
grant all privileges on database otskinter to otskinter;
\c otskinter
create extension hstore;
```

Virtualenv:

```
virtualenv -p /usr/bin/python3 ../venv_dev
. ../venv_dev/bin/activate
pip install -r requirements/dev.txt
```

Commands to setup user/roles:

```
python manage.py setup_user_roles
# python manage.py create_test_users # OPTIONAL
```

Helpers (optional):

1. `cp dev-activate.example.sh dev-activate.sh` (`dev-activate.sh` is git ignored so can be machine specific)
2. edit your `dev-activate.sh` to match machines path etc.
