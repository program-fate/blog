#!uer/bin/env python
# -*- coding: utf-8 -*-
# author: wangwensheng
import socket
import math
from datetime import datetime

from flask import Blueprint, request, render_template, session, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
# 避免循环引入，删掉没用的导包
# from manage import app
from utils.faceRecognition import register_face_user, login_face_user
from utils.functions import is_login
from back.models import User, Category, Article

# 第一步：生成蓝图对象
back_blue = Blueprint('back', __name__)


def select_login_info(username):
    user_list = User.query.filter(User.username == username).all()
    return user_list  # 返回列表形式的参数


@back_blue.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('back/register.html')

    if request.method == 'POST':
        # 获取数据
        user = User()
        username = request.form.get('username')
        password = request.form.get('userpwd')
        password_again = request.form.get('userpwd2')
        face = request.form.get('face').split(',')[-1]
        if not(face and username and password and password_again):
            error = '请填写完整信息'
            return render_template('back/register.html', error=error)
        if password != password_again:
            error = '两次密码输入不一致，请重新输入 '
            return render_template('back/register.html', error=error)
        user_list = select_login_info(username)
        if user_list != []:
            error = '用户名已存在 '
            return render_template('back/register.html', error=error)
        if not register_face_user(face, username):  # 把username当做人脸识别的userId
            error = '注册失败'
            return render_template('back/register.html', error=error)
        user.username = username
        user.password = generate_password_hash(password)
        user.save_update()
        return redirect(url_for('back.login'))


@back_blue.route('/face/', methods=['GET', 'POST'])
def face():
    if request.method == 'GET':
        return render_template('back/face.html')

    if request.method == 'POST':
        face = request.form.get('face').split(',')[-1]
        username = request.form.get('username')
        if not (face and username):
            return render_template('back/face.html',  error='登录信息请填写完整')
        user = User.query.filter(User.username == username).first()
        if not user:
            return render_template('back/face.html',  error='该用户不存在')
        if not login_face_user(face, username):
            return render_template('back/face.html', error='识别失败')
        session['id'] = user.id
        session['username'] = username
        return render_template('back/index.html')


@back_blue.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('back/login.html')

    if request.method == 'POST':
        # 模拟登录
        username = request.form.get('username')
        password = request.form.get('userpwd')
        user_list = select_login_info(username)
        if user_list != []:
            db_user = user_list[0]
            if username == db_user.username and check_password_hash(db_user.password, password):
                # 模拟登录成功，给前端一个标识符(sessionid)，后端校验该标识符
                session['id'] = db_user.id
                session['username'] = username
                # return render_template('back/index.html')
                return redirect(url_for('back.index'))
        error = '账号或密码错误，请重新登录'
        return render_template('back/login.html', error=error)


@back_blue.route('/update_user_info/', methods=['GET', 'POST'])
def update_user_info():
    if request.method == 'GET':
        pass

    if request.method == 'POST':
        db_user = User.query.get(session['id'])
        new_username = request.form.get('username')
        user_list = User.query.filter(User.username == new_username).filter(User.username != session['username']).all()
        if user_list == []:
            old_password = request.form.get('old_password')
            if check_password_hash(db_user.password, old_password):
                password = request.form.get('password')
                new_password = request.form.get('new_password')
                if password == new_password:
                    db_user.username = new_username
                    db_user.password = generate_password_hash(password)
                    db_user.save_update()
                    success = '修改成功，请重新登录'
                    return render_template('back/login.html', success=success)
                    # return redirect(url_for('back.login', success=success))
            error = '密码错误,请重新登录'
            return render_template('back/login.html', error=error)
        # error = '该用户名已存在，请重新输入'
        # return render_template('back/index.html', error=error)


@back_blue.route('/del_session/', methods=['GET', 'POST'])
def del_session():
    if request.method == 'GET':
        db_user = User.query.get(session['id'])
        db_user.last_login_time = datetime.now()
        db_user.login_num = db_user.login_num + 1
        # 获取本机电脑名
        # local_name = socket.getfqdn(socket.gethostname())
        # 获取本机ip
        # last_login_ip = socket.gethostbyname(local_name)
        # db_user.last_login_ip = last_login_ip
        db_user.save_update()
        session.pop('id', None)
        return redirect(url_for('back.login'))


@back_blue.route('/index/', methods=['GET'])
@is_login
def index():
    if request.method == 'GET':
        article_list = Article.query.filter(Article.user_id == session['id']).all()
        # 查询登录成功的登录人的信息
        db_user = User.query.get(session['id'])
        # 动态绑定到request中
        request.username = db_user.username
        request.id = session['id']
        request.password = db_user.password
        if db_user.last_login_time != None:
            request.last_login_time = db_user.last_login_time.strftime('%Y-%m-%d %H:%M:%S')
        request.login_num = db_user.login_num
        request.last_login_ip = db_user.last_login_ip
        # 获取本机电脑名，挂载不支持
        # local_name = socket.getfqdn(socket.gethostname())
        # 获取本机ip
        # login_ip = socket.gethostbyname(local_name)
        # request.login_ip = login_ip
        user_list = User.query.filter().all()
        return render_template('back/index.html',
                               article_list=article_list,
                               user_list=user_list)


def is_category_legal(new_category_name):
    # 查询category_name是否重复
    category_list = Category.query.filter(Category.category_name == new_category_name).all()
    return category_list


# 栏目主页
@back_blue.route('/category/', methods=['GET', 'POST'])
@is_login
def category():
    if request.method == 'GET':
        # 根据用户登录的id找到属于这个用户的所有Category
        category_list = Category.query.filter(Category.user_id == session['id']).all()
        db_user = User.query.get(session['id'])
        request.username = db_user.username
        request.id = session['id']
        request.password = db_user.password
        return render_template('back/category.html',
                               category_list=category_list)

    if request.method == 'POST':
        new_category_name = request.form.get('name')
        category_list = is_category_legal(new_category_name)
        if category_list == []:  # 数据库中没有记录，是新纪录，没有重复
            category = Category()
            category.category_name = request.form.get('name')
            category.category_alias = request.form.get('alias')
            category.category_fid = eval(request.form.get('fid'))
            category.category_keywords = request.form.get('keywords')
            category.category_description = request.form.get('describe')
            category.user_id = session['id']
            category.save_update()
            category_list = Category.query.filter().all()
            return render_template('back/category.html', category_list=category_list)
        print(category_list)
        error = "栏目名'%s'重复，请重新输入" % new_category_name
        category_list = Category.query.filter().all()
        return render_template('back/category.html',
                               category_list=category_list,
                               error=error)


# 删除栏目
@back_blue.route('/del_category/<int:category_id>/', methods=['GET', 'POST'])
@is_login
def del_category(category_id):
    if request.method == 'GET':
        db_category = Category.query.filter(Category.category_id == category_id).all()[0]
        db_category.delete()
        return redirect(url_for('back.category'))


# 更新栏目
@back_blue.route('/update_category/<int:category_id>/', methods=['GET', 'POST'])
@is_login
def update_category(category_id):
    if request.method == 'GET':
        db_category = Category.query.filter(Category.category_id == category_id).all()[0]
        db_user = User.query.get(session['id'])
        request.username = db_user.username
        request.id = session['id']
        request.password = db_user.password
        # 查询父节点不是自己，也不是自己子节点的记录
        category_list = Category.query.filter(Category.category_id != db_category.category_id). \
            filter(Category.category_fid != db_category.category_id).all()
        return render_template('back/update-category.html/',
                               db_category=db_category,
                               category_list=category_list)

    if request.method == 'POST':
        new_category_name = request.form.get('name')
        category_list = Category.query.filter(Category.category_id == new_category_name) \
            .filter(Category.category_id != category_id).all()
        # 根据new_category_name从数据库中取值，取出的若为空列表，则表明新的栏目名在没有重复，可以使用
        if category_list == []:
            # 根据category_name从数据库中取值，进行更新
            db_category = Category.query.filter(Category.category_id == category_id).all()[0]
            db_category.category_name = request.form.get('name')
            db_category.category_alias = request.form.get('alias')
            db_category.category_fid = eval(request.form.get('fid'))
            db_category.category_keywords = request.form.get('keywords')
            db_category.category_description = request.form.get('describe')
            db_category.save_update()
            return redirect(url_for('back.category'))
        error = "栏目名'%s'重复，请重新输入" % new_category_name
        category_list = Category.query.filter().all()
        # print(category_list)
        db_category = Category.query.filter(Category.category_id == category_id).all()[0]
        return render_template('back/update-category.html/',
                               db_category=db_category,
                               category_list=category_list,
                               error=error)


def get_article_json(article_list):
    article_dic = {}
    article_dict = {}
    for i, art_obj in enumerate(article_list):
        article_dic["article_id"] = art_obj.article_id
        article_dic["article_title"] = art_obj.article_title
        article_dic["category_id"] = art_obj.category_id
        article_dic["article_label"] = art_obj.article_label
        article_dic["write_time"] = art_obj.write_time.strftime('%Y-%m-%d %H:%M:%S')
        article_dict[str(i)] = {"article_id": article_dic["article_id"],
                                "article_title": article_dic["article_title"],
                                "category_id": article_dic["category_id"],
                                "article_label": article_dic["article_label"],
                                "write_time": article_dic["write_time"]}
    print(article_dict)
    return article_dict


# 加载文章页面
@back_blue.route('/article/', methods=['GET', 'POST'])
@is_login
def article():
    if request.method == 'GET':
        db_user = User.query.get(session['id'])
        request.username = db_user.username
        request.id = session['id']
        request.password = db_user.password
        page = request.form.get('page')
        article_list = Article.query.filter(Article.user_id == session['id']).all()
        length = len(article_list)
        page_count = math.ceil(length / 7)
        page_list = [ i for i in range(1,page_count+1) ]
        if page == None:
            page = 1
        if page_list == [] :
            page_list = [1]
        article_list = Article.query.filter(Article.user_id == session['id']).offset((page - 1) * 7).limit(7).all()
        return render_template('back/article.html',
                               article_list=article_list,
                               page_list=page_list)

    if request.method == 'POST':
        # 判断是否是删除数据申请，否则是删除数据
        if 'article_id' in request.get_data().decode():
            article_id = int(request.get_data().decode().split('=')[-1])
            db_article = Article.query.get(article_id)
            db_article.delete()
            article_list = Article.query.filter(Article.user_id == session['id']).all()
            length = len(article_list)
            page_count = math.ceil(length / 7)
            article_dict = get_article_json(article_list)
            article_dict['page_count'] = page_count
            return jsonify(article_dict)
        # 分页
        page = eval(request.form.get('page'))
        article_list = Article.query.filter(Article.user_id == session['id']).offset((page - 1) * 7).limit(7).all()
        article_dict = get_article_json(article_list)
        return jsonify(article_dict)


# 新增文章
@back_blue.route('/add_article/', methods=['GET', 'POST'])
@is_login
def add_article():
    if request.method == 'GET':
        db_user = User.query.get(session['id'])
        request.username = db_user.username
        request.id = session['id']
        request.password = db_user.password
        db_category = Category.query.filter(Category.user_id == session['id']).all()
        return render_template('back/add-article.html', db_category=db_category)

    if request.method == 'POST':
        article = Article()
        article.article_content = request.form.get('content')
        if article.article_content:
            article.article_title = request.form.get('title')
            article.article_keywords = request.form.get('keywords')
            article.article_description = request.form.get('describe')
            article.category_id = request.form.get('category')
            article.article_image = request.form.get('titlepic')
            article.article_label = request.form.get('tags')
            article.article_status = eval(request.form.get('visibility'))
            article.user_id = session['id']
            article.save_update()
            return redirect(url_for('back.article'))
        error = '文章内容不能为空'
        db_category = Category.query.filter(Category.user_id == session['id']).all()
        return render_template('back/add-article.html',
                               db_category=db_category,
                               error=error)


# 删除文章
# @back_blue.route('/del_article/<int:article_id>/', methods=['GET'])
# @is_login
# def del_article(article_id):
#     if request.method == 'GET':
#         db_article = Article.query.get(article_id)
#         db_article.delete()
#         return redirect(url_for('back.article'))


# 更新文章
@back_blue.route('/update_article/<int:article_id>/', methods=['GET', 'POST'])
@is_login
def update_article(article_id):
    if request.method == 'GET':
        db_user = User.query.get(session['id'])
        request.username = db_user.username
        request.id = session['id']
        request.password = db_user.password
        db_article = Article.query.get(article_id)
        category_list = Category.query.filter().all()
        return render_template('back/update-article.html',
                               db_article=db_article,
                               category_list=category_list)

    if request.method == 'POST':
        db_article = Article.query.get(article_id)
        db_article.article_content = request.form.get('content')
        if db_article.article_content:
            db_article.article_title = request.form.get('title')
            db_article.article_keywords = request.form.get('keywords')
            db_article.article_description = request.form.get('describe')
            db_article.category_id = request.form.get('category')
            db_article.article_image = request.form.get('titlepic')
            db_article.article_label = request.form.get('tags')
            db_article.article_status = eval(request.form.get('visibility'))
            db_article.save_update()
            # 从数据库中获取article更新后的属性
            db_article = Article.query.get(article_id)
            category_list = Category.query.filter().all()
            return render_template('back/update-article.html',
                                   db_article=db_article,
                                   category_list=category_list)
        error = '文章内容不能为空'
        db_article = Article.query.get(article_id)
        category_list = Category.query.filter().all()
        return render_template('back/update-article.html',
                               db_article=db_article,
                               category_list=category_list,
                               error=error)
