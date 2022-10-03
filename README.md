# Yatube

[![CI](https://github.com/BU-Marina/Yatube/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/BU-Marina/Yatube/actions/workflows/python-app.yml)

Социальная сеть для просмотра постов на Django

## Описание

Yatube - социальная сеть, в которой можно создать учетную запись, публиковать посты, подписываться на любимых авторов и комментировать их записи.

## Технологии

    Python 3.7.9
    Django==2.2.16
    mixer==7.1.2
    Pillow==8.3.1
    pytest==6.2.4
    pytest-django==4.4.0
    pytest-pythonpath==0.7.3
    requests==2.26.0
    six==1.16.0
    sorl-thumbnail==12.7.0
    Faker==12.0.1

### Как запустить проект в dev-режиме:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Marina-ui/Yatube
```

```
cd Yatube
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции из директории с файлом manage.py:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```

Запуск тестов из директории Yatube:

```
pytest
```

### Заполнить БД:

```
python3 manage.py shell  
```

Выполнить в открывшемся терминале:

>>> from django.contrib.contenttypes.models import ContentType
>>> ContentType.objects.all().delete()
>>> quit()

python manage.py loaddata dump.json 
