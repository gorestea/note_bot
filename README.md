```sh
git clone
```

Создать бота через BotFather, получить токен бота. Добавить через BotFather инструкцию о командах бота (/mynotes, /addnote) (необязательно)


Если локально:

1.
```sh
pip install -r requirements.txt
```
2. Изменить файл .env

3. Запустить bot.py


Если через докер:

1. Изменить файл .env (свой бот, свой tg api id, свой tg api hash)

2.
```sh
docket-compose up --build
```


