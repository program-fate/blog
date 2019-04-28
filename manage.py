#!uer/bin/env python
# -*- coding: utf-8 -*-
# author: wangwensheng
from flask import Flask
from flask_script import Manager

from back.models import db
from back.views import back_blue
from web.views import web_blue

app = Flask(__name__)

app.secret_key='asd.546@asd165'

app.register_blueprint(blueprint=back_blue, url_prefix='/back')
app.register_blueprint(blueprint=web_blue, url_prefix='/web')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:rock1204@120.78.69.6:3306/blog'
db.init_app(app)


if __name__ == '__main__':
    manage = Manager(app)
    manage.run()
