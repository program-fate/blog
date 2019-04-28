#!uer/bin/env python
# -*- coding: utf-8 -*-
# author: wangwensheng

from aip import AipFace

APP_ID = '16107082'
API_KEY = 'pVw0XbDKLqgFPgZtjVEbkiem'
SECRET_KEY = 'DeFewaZrLVrXSHOI7MCzjtFPvnHp959c'

client = AipFace(APP_ID, API_KEY, SECRET_KEY)


def register_face_user(image, user_id, image_type='BASE64' , group_id='user'):
    # 人脸注册
    response = client.addUser(image, image_type, group_id, user_id)
    return False if response['error_code'] else True



""" 调用人脸搜索 """
# username传过来当作百度云的user_id使用
def login_face_user(image, user_id, image_type='BASE64', group_id_list= "user"):
    response = client.search(image, image_type, group_id_list )
    print(response)
    if response['result']['user_list'][0]['score'] > 80 and user_id == response['result'][ 'user_list'][0]['user_id']:
        return True
    return False
