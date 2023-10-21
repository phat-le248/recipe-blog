# Food Recipe project

## 1. Description
This is a complete function recipe blog where you can share your recipes and create menus. No more struggling to think what to eat each day, Recipe Blog got you cover

![ui-img](https://i.postimg.cc/jjZ1yfZD/ezgif-com-gif-maker.gif)

## 2. Install and run
- Clone project and set up enviroment

`git clone https://github.com/phat-le248/recipe-blog ./recipe-blog`

`cd recipe-blog`

`sudo apt install python3-virtualenv`

`virtualenv venv`

- Install packages support for mysqlclient (more info: https://pypi.org/project/mysqlclient/)

`sudo apt-get install python3-dev default-libmysqlclient-dev build-essential`

- Install python packages needed for project

`pip install -r requirements.txt`

- Install mysql server (more info: https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-20-04)

`sudo apt update`

`sudo apt install mysql-server`

`sudo mysql`

`ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'password';` # replace password if needed

`exit`

`sudo mysql_secure_installation`

- Set up enviroment variables (update later)

- Run application
`export FLASK_APP=main.py`

`flask setup`

`flask --app main.py run`

## 3. Credit

## 4. License
