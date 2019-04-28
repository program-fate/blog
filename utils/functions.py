#!uer/bin/env python
# -*- coding: utf-8 -*-
# author: wangwensheng

# 外层函数嵌套内层函数
# 外层函数返回内存函数
# 内层函数调用外层函数的参数
from functools import wraps

from flask import session, redirect, url_for

def is_login(func):
    @wraps(func)  # 把调用装饰的函数的名字，重新改回自己的名字
    def check(*args, **kwargs):
        try:
            # 登录情况
            # func()为被login_require装饰的函数
            id = session['id']
            if not id:
                return redirect(url_for('back.login'))
            return func(*args, **kwargs)
        except Exception as e :
            print(e)
            # 没登录成功
            return redirect(url_for('back.login'))
            # return render_template('back/login.html')
    return check
