#!uer/bin/env python
# -*- coding: utf-8 -*-
# author: wangwensheng
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_tables():
    db.create_all()


class User(db.Model):
    # 定义自增的主键id字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 定义可变长度为10，且唯一的name字段
    username = db.Column(db.String(11), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    last_login_time = db.Column(db.DateTime, default=datetime.now)
    login_num = db.Column(db.Integer, default=0)
    last_login_ip = db.Column(db.String(32))
    is_delete = db.Column(db.Boolean, default=False)
    # 关联数据库中表名为stu的表
    # tablename 不写，则表示模型对应的表名称为模型名的小写
    __tablename__ = 'user'

    def save_update(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Category(db.Model):
    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(20), nullable=False, unique=True)
    category_alias = db.Column(db.String(10))
    category_fid = db.Column(db.String(20))
    category_keywords = db.Column(db.String(10))
    category_description = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    __tablename__ = 'category'

    def save_update(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Article(db.Model):
    article_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_title = db.Column(db.String(30), nullable=False)
    article_content = db.Column(db.Text, nullable=False)
    article_keywords = db.Column(db.String(30))
    article_description = db.Column(db.String(100))
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'))
    article_label = db.Column(db.String(30))
    article_image = db.Column(db.String(50))
    article_status = db.Column(db.Integer, default=1)
    write_time = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ctgr = db.relationship('Category', backref='ar')
    __tablename__ = 'article'

    def save_update(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
