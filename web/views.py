#!uer/bin/env python
# -*- coding: utf-8 -*-
# author: wangwensheng
import math
import time
from datetime import datetime

from flask import Blueprint, request, render_template, redirect, url_for, jsonify

# 第一步：生成蓝图对象
from back.models import Article, Category

web_blue = Blueprint('web', __name__)

def common_content():
    article_list = Article.query.filter().all()
    category_list = Category.query.filter().all()
    length = len(article_list)
    page_count = math.ceil(length / 5)
    page_list = [i for i in range(1, page_count + 1)]
    page = 1
    if page_list == []:
        page_list = [1]
    article_list = Article.query.offset((page - 1) * 5).limit(5).all()
    return article_list, category_list, page_list


def get_article_json(article_list):
    article_dic = {}
    article_dict = {}
    for i, art_obj in enumerate(article_list):
        article_dic["article_title"] = art_obj.article_title
        article_dic["article_content"] = art_obj.article_content
        article_dict[str(i)] = {"article_title": article_dic["article_title"],
                                "article_content": article_dic["article_content"]
                                }
    print(article_dict)
    return article_dict

#
@web_blue.route('/index/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        article_list, category_list, page_list = common_content()
        return render_template('web/index.html',
                               article_list=article_list,
                               category_list=category_list,
                               page_list=page_list)

    if request.method == 'POST':
        page = eval(request.get_data().decode().split('=')[-1])
        article_list = Article.query.offset((page - 1) * 5).limit(5).all()
        article_dict = get_article_json(article_list)
        return jsonify(article_dict)


@web_blue.route('/list/', methods=['GET', 'POST'])
def list():
    if request.method == 'GET':
        article_list, category_list, page_list = common_content()
        return render_template('web/list.html',
                               article_list=article_list,
                               category_list=category_list,
                               page_list=page_list)

    if request.method == 'POST':
        page = eval(request.get_data().decode().split('=')[-1])
        article_list = Article.query.offset((page - 1) * 5).limit(5).all()
        article_dict = get_article_json(article_list)
        return jsonify(article_dict)



@web_blue.route('/about/', methods=['GET', 'POST'])
def about():
    category_list = Category.query.filter().all()
    return render_template('web/about.html',
                           category_list=category_list)


@web_blue.route('/info/', methods=['GET', 'POST'])
def info():
    if request.method == 'GET':
        today = time.strftime("%Y-%m-%d", time.localtime())
        request.today = today
        category_list = Category.query.filter().all()
        return render_template('web/info.html',
                               category_list=category_list)


@web_blue.route('/info/<int:category_id>/', methods=['GET', 'POST'])
def info_content(category_id):
    if request.method == 'GET':
        today = time.strftime("%Y-%m-%d", time.localtime())
        request.today = today
        category_list = Category.query.filter().all()
        article_list = Article.query.filter(Article.category_id == category_id).all()
        return render_template('web/info.html',
                               article_list=article_list,
                               category_list=category_list)


@web_blue.route('/info_article/<int:article_id>/', methods=['GET', 'POST'])
def article_content(article_id):
    if request.method == 'GET':
        today = time.strftime("%Y-%m-%d", time.localtime())
        request.today = today
        category_list = Category.query.filter().all()
        article_list = Article.query.filter(Article.article_id == article_id).all()
        return render_template('web/info.html',
                               article_list=article_list,
                               category_list=category_list)
