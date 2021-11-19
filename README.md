# bank_coins_parser

Парсинг монет на сайтах Челиндбанка, Челябинвеста, Уралсиба и Сбербанка

Программа написана с помощью фреймворка Django. Все спарсенные данные выгружаются в таблицу, новые монеты отправляют сообщения в телеграм

# Как запустить:
  pip install -r requirements.txt
  python manage.py Parse_bank
  python manage.py runserver
