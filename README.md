# Тестовое задание для КиберЗоны РТУ МИРЭА

### Направление: backend
### Стек технологий: Python, FastAPI, postgreSQL, Docker

Это простейшая апишка для бронирования. По сути полное соответствие требованиям.
CRUD с проверкой данных и контейнеризацией через docker.

# Способы запуска

## Через git
`git clone https://github.com/moscow-intelligent/CyberZoneTest.git`
<br>
`cd CyberZoneTest`
<br>
`python3 -m pip install -r requirements.txt`
<br>
- Ubuntu
`sudo apt-get install postgresql`<br>
- Arch/Manjaro `pacman -Syu postgresql`<br>

`psql --command "CREATE USER cyberuser WITH PASSWORD 'cyberpassword';"`
<br>
`psql --command "CREATE DATABASE cyberapi WITH OWNER cyberuser;"`
<br>
Изменить переменную `DATABASE_URL` на `DATABASE_URL = 'postgresql://cyberuser:cyberpassword@localhost/cyberapi'`
<br>
`uvicorn main:app --host 0.0.0.0 --port 8000`
<br>

## Через docker
`git clone https://github.com/moscow-intelligent/CyberZoneTest.git`
<br>
`cd CyberZoneTest`
<br>
`docker-compose build`
<br>
`docker-compose up`

Документация доступна по ссылке https://localhost:8000/docs после развертывания проекта

## Тесты

Тесты лежат в `test.py`, для запуска нужно поменять переменную на валидный адрес базы данных и запустить `pip install pytest`, `pytest test.py`


