# Telegram-бот для продаж

Бот для продажи продукции из интернет-магазина на базе CMS [elasticpath](https://www.elasticpath.com/) через API сервиса.

Пример работающего бота: [@DvmnFishSellerBot](https://t.me/DvmnFishSellerBot)

![image](https://dvmn.org/media/filer_public/0a/5b/0a5b562c-7cb4-43e3-b51b-1b61721200fb/fish-shop.gif)

## Установка

Скачайте файлы из репозитория. Python3 должен быть уже установлен. 

Затем используйте `pip` (или `pip3`) для установки зависимостей:
```
pip install -r requirements.txt
```
Помимо этого, для работы понадобится создать файл `.env` в корневом каталоге проекта. Данный файл необходим для работы с переменными окружения и должен содержать в себе переменные: 
```
CLIENT_SECRET=<ключ клиента в CMS elasticpath>
CLIENT_ID=<id клиента в CMS elasticpath>
TELEGRAM_TOKEN=<SUPPORT_BOT_TELEGRAM_TOKEN>
DATABASE_PASSWORD=<REDIS DATABASE PASSWORD>
DATABASE_HOST=<адрес хоста Redis>
DATABASE_PORT=<порт Redis DB (указан после двоеточия в Public endpoint)>
```

Для получения `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_PASSWORD` необходимо создать базу на [Redis](https://redis.com/). Все нужные параметры находятся на вкладке конфигурации БД:

![image](https://github.com/dmitriev-ilya/quiz_bot/assets/67222917/bb67d02d-5e9b-4c9c-acd3-a82731903668)

Также необходимо создать Telegram-бота для получения `TELEGRAM_TOKEN`. Для этого нужно обратиться к [@BotFather](https://telegram.me/BotFather). Подробная инструкция по настройке и созданию бота приведена здесь - [Инструкция по созданию Telegram-бота](https://way23.ru/%D1%80%D0%B5%D0%B3%D0%B8%D1%81%D1%82%D1%80%D0%B0%D1%86%D0%B8%D1%8F-%D0%B1%D0%BE%D1%82%D0%B0-%D0%B2-telegram.html)

Для получения `CLIENT_SECRET` и `CLIENT_ID` нужно зарагестрироваться на сайте [elasticpath](https://www.elasticpath.com/) и следовать [туториалу](https://elasticpath.dev/docs/commerce-cloud/authentication/application-keys/create-an-application-key).

## Использование скрипта

Для запуска бота в консоли, находясь в папке с проектом, используйте следующую команду:

```
python3 tg_bot.py
```
