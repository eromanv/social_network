# Проект «API для Yatube»
## Приложение предоставляет доступ к своим данным клиентскому приложению по определенному URL.
## API и документация для приложения Yatube

### Стек технологий:
Python,
Djando,
DRF
Описание

### Данное API позволяет использовать следующий функционал:
1. Публикации

Получать список всех публикаций
Создавать новую публикацию
Полностью или частично редактировать публикацию
Удалять публикацию
2. Сообщества

Получение списка доступных сообществ
Получение информации о сообществе
3. Комментарии

Получение всех комментариев к публикации
Получение конкретного комментария к публикации
Добавление нового комментария к публикации
4. Подписка

Список всех подписчиков
Подписка на публикации других пользователей

## Как установить и запустить
Чтобы запустить это приложение, вам потребуeтся установленный на вашем компьютере Git.
Клонировать репозиторий:
```git clone https://github.com/sniki-ld/api_final_yatube.git```
Перейти в него в командной строке:
```cd api_final_yatube```
Cоздать и активировать виртуальное окружение:
```
python3 -m venv env
source env/bin/activate
```
Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```
Выполнить миграции:
```
python3 manage.py migrate
```
Запустить проект:
```
python3 manage.py runserver
```
Перейти:

http://127.0.0.1:8000/

## Как можно его использовать:

Для аутентификации используются JWT-токены.
Информация доступна как для незарегистрированных пользователей (доступ к API только на чтение), так и для зарегистрированных.

Более подробное описание API можно получить по адресу:
http://localhost:8000/redoc/

