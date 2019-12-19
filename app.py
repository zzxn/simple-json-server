#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request
from util import log
from flask_cors import CORS
from flask import current_app
import json
import uuid
import time
import jieba
from typing import List

app = Flask(__name__)
CORS(app)

with open('data/articles.json', encoding='utf-8') as f:
    article_data: list = json.load(f)

with open('data/user.json', encoding='utf-8') as f:
    user_data: list = json.load(f)

with open('data/classname.json', encoding='utf-8') as f:
    classname_list: list = json.load(f)


def response(data=None, code: str = '200', error_type: str = None, error_message: str = None):
    res = {'code': code}
    if error_type is not None or error_message is not None:
        res['error'] = {
            'type': error_type,
            'message': error_message
        }
    if data is not None:
        res['data'] = data
    return res


NOT_FOUND_ERROR_RESPONSE = response(code='404', error_type='not found', error_message='找不到资源')


def get_user_by_id(user_id: str):
    for user in user_data:
        if user_id == user['id']:
            return user
    return None


@app.route('/')
@log
def hello_world():
    return 'Hello World!'


# @app.after_request
# def after_request(response):
#     response.headers['Access-Control-Allow-Origin'] = '*'
#     return response


@app.route('/api/store')
def store():
    with open('data/articles.json', 'w', encoding='utf-8') as f:
        json.dump(article_data, f, ensure_ascii=False)

    with open('data/user.json', 'w', encoding='utf-8') as f:
        json.dump(article_data, f, ensure_ascii=False)

    with open('data/classname.json', 'w', encoding='utf-8') as f:
        json.dump(classname_list, f, ensure_ascii=False)


# ********************** user related **********************

@app.route('/api/user/login', methods=['POST'])
def login():
    data = json.loads(request.get_data(as_text=True))
    print(data)
    for user in user_data:
        if user['username'] == data['username'] and user['password'] == data['password']:
            return response({
                'id': user['id'],
                'group_id': user['group_id'],
                'token': json.dumps(user)
            })
    return NOT_FOUND_ERROR_RESPONSE


@app.route('/api/user/register', methods=['POST'])
def register():
    data = json.loads(request.get_data(as_text=True))
    for user in user_data:
        if user['username'] == data['username']:
            return response(code='404', error_type='duplicate')

    new_user = {
        'id': str(uuid.uuid4()).replace('-', ''),
        'username': data['username'],
        'password': data['password'],
        'group_id': "1"
    }
    user_data.append(new_user)
    return response({
        'id': new_user['id'],
        'group_id': new_user['group_id'],
        'token': json.dumps(new_user)
    })


@app.route('/api/user/modify', methods=['POST'])
def modify_user_info():
    data = json.loads(request.get_data(as_text=True))
    print(data)
    for user in user_data:
        if user['id'] == data['id']:
            if 'username' in data.keys() and data['username'].strip() != '':
                user['username'] = data['username']
                print('change username!')
            if 'password' in data.keys() and data['password'].strip() != '':
                user['password'] = data['password']
                print('change password!')
            return response()

    return NOT_FOUND_ERROR_RESPONSE


# ********************** article related **********************


@app.route('/api/article/', methods=['POST'])
def post_article():
    data: dict = json.loads(request.get_data(as_text=True))
    data.setdefault('classname', None)
    data.setdefault('labels', None)
    if data['classname'] is not None and data['classname'] not in classname_list:
        classname_list.append(data['classname'])
    if 'id' in data.keys() and data['id'] is not None and not data['id'].isspace():
        return modify_article(data)
    article = {
        'id': str(len(article_data) + 1),
        'title': data['title'],
        'text': data['text'],
        'classname': data['classname'],
        'labels': data['labels'],
        'view_number': 0,
        'like_number': 0,
        'comment_number': 0,
        'comments': []
    }
    article_data.append(article)
    return response({'id': article['id']})


def modify_article(data):
    for article in article_data:
        if data['id'] == article['id']:
            if data['title'] is not None:
                article['title'] = data['title']
            if data['text'] is not None:
                article['text'] = data['text']
            if data['classname'] is not None:
                article['classname'] = data['classname']
            if data['labels'] is not None:
                article['labels'] = data['labels']
            return response({'id': article['id']})
    return NOT_FOUND_ERROR_RESPONSE


@app.route('/api/article/<article_id>/', methods=['DELETE', 'GET'])
def delete_or_get_article_by_id(article_id):
    if request.method == 'DELETE':
        global article_data
        print(article_id)
        article_data = [article for article in article_data if article['id'] != article_id]
        return response()
    else:
        article = [article for article in article_data if article['id'] == article_id]
        return response(article[0]) if len(article) > 0 else NOT_FOUND_ERROR_RESPONSE


@app.route('/api/article/', methods=['GET'])
def get_all_articles():
    index = int(request.args.get('index', 0))
    size = int(request.args.get('size', len(article_data)))
    classname = request.args.get('classname', None)

    page = article_data
    if classname not in (None, ''):
        page = [article for article in page if article['classname'] == classname]
    page = page[index:index + size]
    page.reverse()
    print(page.__len__())
    return response(page)


# TODO: 临时加的api！
@app.route('/api/article/total', methods=['GET'])
def get_article_total():
    classname = request.args.get('classname', None)
    page = article_data
    if classname not in (None, ''):
        page = [article for article in page if article['classname'] == classname]

    return response({
        'total': len(page)
    })


@app.route('/api/article/<article_id>/view', methods=['POST'])
def increment_view(article_id):
    for article in article_data:
        if article_id == article['id']:
            article['view_number'] += 1
            return response({'view_number': article['view_number']})
    return NOT_FOUND_ERROR_RESPONSE


@app.route('/api/article/<article_id>/like', methods=['POST'])
def increment_like(article_id):
    for article in article_data:
        if article_id == article['id']:
            article['like_number'] += 1
            return response({'like_number': article['like_number']})
    return NOT_FOUND_ERROR_RESPONSE


@app.route('/api/article/<article_id>/comment', methods=['POST'])
def comment(article_id):
    data: dict = json.loads(request.get_data(as_text=True))
    if 'text' not in data.keys():
        return response(code='404', error_type='bad request', error_message='评论不能为空')
    data.setdefault('user_id', '084f47b675824bc38d0c5043ffba7a30')
    for article in article_data:
        if article_id == article['id']:
            article['comments'].append({
                'user_id': data['user_id'],
                'text': data['text'],
                'time': int(time.time())
            })
            article['comment_number'] = len(article['comments'])
            return response()
    return NOT_FOUND_ERROR_RESPONSE


@app.route('/api/article/<article_id>/comment', methods=['GET'])
def get_comment(article_id):
    index = int(request.args.get('index', 0))
    size = int(request.args.get('size', 100))

    for article in article_data:
        if article_id == article['id']:
            page = article['comments'][index:index + size]
            for e in page:
                e['username'] = get_user_by_id(e['user_id'])['username']
            page.reverse()
            return response(page)
    return NOT_FOUND_ERROR_RESPONSE


def kw_list_match(kw_list: List[str], text: str) -> bool:
    for kw in kw_list:
        if text.find(kw) != -1:
            return True
    return False


@app.route('/api/article/search', methods=['GET'])
def search_article():
    index = request.args.get('index', 0)
    size = request.args.get('size', len(article_data))
    classname = request.args.get('classname', None)
    keyword = request.args.get('keyword', '').strip()

    if keyword == '':
        return response(code='404', error_type='bad request', error_message='关键词不能为空')

    kw_list = list(jieba.cut_for_search(keyword))
    if classname is not None:
        result = [article for article in article_data
                  if article['classname'] == classname and kw_list_match(kw_list, article['text'])]
    else:
        result = [article for article in article_data if kw_list_match(kw_list, article['text'])]
    current_app.logger.debug('Search kws: ' + str(kw_list) + ' and get %d results.' % len(result))
    page = result[index:index + size]
    return response(page)


@app.route('/api/article/classname', methods=['GET'])
def get_classname():
    return response(classname_list)


@app.route('/api/article/classname/<classname>', methods=['DELETE'])
def delete_classname(classname):
    for article in article_data:
        if article['classname'] == classname:
            article['classname'] = None
    classname_list.remove(classname)
    return response()


if __name__ == '__main__':
    app.run()
