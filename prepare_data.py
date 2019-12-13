#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import json
import jieba.analyse

class_candidate = ['科技', '互联网', '政治', '新闻']
label_number = 5
raw_path = 'data/raw.json'
out_path = 'data/articles.json'

if __name__ == '__main__':
    with open(raw_path, encoding='utf-8') as f:
        raw_data = json.load(f)
        article_data = [{
            'id': str(article_id),
            'title': article['title'],
            'text': article['text'],
            'view_number': random.randint(0, 20),
            'like_number': random.randint(0, 20),
            'comment_number': 0,
            'classname': class_candidate[random.randint(0, len(class_candidate)) - 1],
            'labels': jieba.analyse.extract_tags(article['text'], topK=label_number),
            'comments': []
        } for (article_id, article) in zip(range(1, len(raw_data)), raw_data)]

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(article_data, f, ensure_ascii=False)
