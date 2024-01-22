# muzej2

## Prerequisites

You will need a db.sqlite3 local database with museum collection data. Ask around.

Also you will need a properly setup local_settings.py file in order to run. Ask around.

## Local development setup

Create virtual env:

```
python -m venv
```

Activate venv:

```
source venv/bin/activate
```

Install packages:

```
pip3 install -r requirements.txt
```

Create migrations (optional - if they are not yet created):

```
python3 manage.py makemigrations
python3 manage.py makemigrations inventura
python3 manage.py makemigrations evidenca
```

Run migrations:

```
python3 manage.py migrate
```

Setup styles:

python manage.py tailwind install

Run Django:

```
python3 manage.py runserver
```

Open separate shell. Run tailwind server (optional - only if you plan to change styles):

```
python manage.py tailwind start
```
