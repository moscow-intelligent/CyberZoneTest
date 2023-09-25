# Тестовое задание для КиберЗоны РТУ МИРЭА

### Направление: backend
### Стек технологий: Python, FastAPI, postgreSQL, Docker

Это простейшая апишка для бронирования. По сути полное соответствие требованиям.
CRUD с проверкой данных и контейнеризацией через docker.

# Способы запуска

## Через git
`git clone https://github.com/moscow-intelligent/CyberZoneTest`
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
`uvicorn main:app --host 0.0.0.0 --port 8000`
<br>

## Через docker
Later...

Документация доступна по [ссылке](localhost:8000/docs) после развертывания проекта


