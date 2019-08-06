#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import logging
import os
from datetime import datetime
from itertools import chain

import requests
from entities.answer import Answer
from entities.question import Question
from lxml import html
from lxml.etree import tostring

# create logger
cli_logger = logging.getLogger('i-otvet-parser')
# set logging level
cli_logger.setLevel(logging.DEBUG)
# create console and file handler
ch = logging.StreamHandler()
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to handlers
ch.setFormatter(formatter)
# add handlers to logger
cli_logger.addHandler(ch)

root = "/home/dinir/Documents/git/xls-graber/"
q_file = "resources/questions.csv"
fin_q_file = q_file
cat_file = "resources/categories.csv"

q_id = 1
c_id = 1
last_free_row = 2

qs_x = "//div[contains(@class, 'qa-q-list')]/div[contains(@class, 'qa-q-list-item')]/div[contains(@class, 'qa-q-item-main')]/div[contains(@class, 'qa-q-item-title')]/a"
q_block_x = "//div[contains(@class, 'qa-part-q-view')]//div[contains(@class, 'qa-q-view-main')]"
q_title_x = "//div[contains(@class, 'qa-main-heading')]/h1/a/span"
q_content_x = "./form/div[contains(@class, 'qa-q-view-content')]/div[contains(@itemprop, 'text')]"
q_tags_x = "./form/div[contains(@class, 'qa-q-view-tags')]" \
           "/ul[contains(@class, 'qa-q-view-tag-list')]" \
           "/li[contains(@class, 'qa-q-view-tag-item')]/a"
q_date_x = "./form/span[contains(@class, 'qa-q-view-avatar-meta')]/span" \
           "/span[contains(@class, 'qa-q-view-when')]" \
           "/span[contains(@class, 'qa-q-view-when-data')]/time"
q_username_x = "./form/span[contains(@class, 'qa-q-view-avatar-meta')]/span" \
               "/span[contains(@class, 'qa-q-view-who')]" \
               "/span[contains(@class, 'qa-q-view-who-data')]/span/a/span[contains(@itemprop, 'name')]"
q_category_x = "./form/span[contains(@class, 'qa-q-view-avatar-meta')]/span" \
               "/span[contains(@class, 'qa-q-view-where')]" \
               "/span[contains(@class, 'qa-q-view-where-data')]/a"

answers_x = "//div[contains(@class, 'qa-part-a-list')]/div[contains(@class, 'qa-a-list')]/div[contains(@class, 'qa-a-list-item')]/div[contains(@class, 'qa-a-item-main')]"
ans_next_page_x = "//li[contains(@class, 'qa-page-links-item')]/a[contains(@class, 'qa-page-next')]"

ans_content_x = "./form/div[contains(@class, 'qa-a-item-content')]/div[contains(@itemprop, 'text')]"
ans_date_x = "./form//span[contains(@class, 'qa-a-item-avatar-meta')]/span" \
             "/span[contains(@class, 'qa-a-item-when')]" \
             "/span[contains(@class, 'qa-a-item-when-data')]/time"
ans_username_x = "./form//span[contains(@class, 'qa-a-item-avatar-meta')]/span" \
                 "/span[contains(@class, 'qa-a-item-who')]" \
                 "/span[contains(@class, 'qa-a-item-who-data')]/span/a/span[contains(@itemprop, 'name')]"

date_p = "%Y-%m-%dT%H:%M:%S%z"
date_f = "%m/%d/%Y %H:%M:%S"

host = "https://i-otvet.ru"
next_page = host + "/questions"
last_page_num = 10925381

q_list = []
a_list = []
c_dict = dict()

fieldnames = ['Id', 'Type', 'ParentIdInFile', 'ParentIdInSIte', 'Title', 'Content',
              'Format', 'CategoryId', 'CategoryUrl', 'Tags', 'UserName',
              'AnonymousName', 'Notify', 'ExtraValue', 'DateTimeFrom', 'DateTimeTo', 'Selected']

cat_filecsv = open(os.path.join(root, cat_file), 'w', newline='', encoding='utf-8')


def add_header():
    spamwriter = csv.writer(q_filecsv, delimiter=',', quotechar='|', quoting=csv.QUOTE_ALL)
    spamwriter.writerow(fieldnames)


def write_in_csv(i):
    global q_filecsv
    global q_file
    global q_list
    global a_list

    q_file = fin_q_file[0:10] + str(i) + '-' + fin_q_file[10:]
    q_filecsv = open(os.path.join(root, q_file), 'w', newline='', encoding='utf-8')
    cli_logger.warn(q_file + " is created")
    add_header()

    add_ques()
    add_ans()
    cli_logger.warn("Added questions in " + q_file)
    q_list = []
    a_list = []

    q_filecsv.close()
    cli_logger.warn(q_file + " is saved")


def process_list_page(l_link):
    if (l_link == (next_page + "?start=" + str(0))):
        l_link = next_page

    tree = get_tree(l_link)
    # get question elements
    questions = tree.xpath(qs_x)
    # get links from elements

    for q in questions:
        que_link = host + q.attrib.get('href')[1:]
        process_q_page(que_link)

    cli_logger.info(l_link)


def process_q_page(q_link):
    global q_id
    tree = get_tree(q_link)

    # grab answer title
    title = tree.xpath(q_title_x)[0].text

    # grab question block
    q_block = tree.xpath(q_block_x)[0]
    # grab q_block content
    content_el = q_block.xpath(q_content_x)
    content = ''
    if (len(content_el) != 0):
        content = stringify_children(content_el[0])
    # grab q_block datetime 
    datetime_from = get_date(q_block.xpath(q_date_x)[0].attrib.get('datetime'))
    # grab q_block tags
    tags = ""  # remove redundant field
    # grab q_block username
    user_el = q_block.xpath(q_username_x)
    username = 'аноним'
    if (len(user_el) != 0):
        username = user_el[0].text
    # grab q_block category
    cat_el = q_block.xpath(q_category_x)
    category_id = ''
    if (len(cat_el) != 0):
        category_id = get_id(cat_el[0].text)

    q_list.append(Question(q_id=q_id, title=title, tags=tags, username=username,
                           datetime_from=datetime_from, content=content, cat_id=category_id))
    process_answers(q_id, tree)

    q_id = q_id + 1


def add_ques():
    spamwriter = csv.writer(q_filecsv, delimiter=',', quotechar='|', quoting=csv.QUOTE_ALL)
    for q in q_list:
        spamwriter.writerow([q.q_id, 'Q', '', '',  # 'Id', 'Type', 'ParentIdInFile', 'ParentIdInSIte'
                             q.title, q.content, 'html',  # 'Title', 'Content', 'Format',
                             q.cat_id, '',  # 'CategoryId', 'CategoryUrl'
                             q.tags, '', q.username,  # 'Tags', 'UserName',
                             '', '',  # 'AnonymousName', 'Notify', 'ExtraValue',
                             q.datetime_from, '', ''])  # 'DateTimeFrom', 'DateTimeTo', 'Selected'


def process_answers(p_id, tree):
    answers = tree.xpath(answers_x)
    for ans in answers:
        # grab ans content
        content_el = ans.xpath(ans_content_x)
        content = ''
        if (len(content_el) != 0):
            content = stringify_children(content_el[0])
        # grab ans datetime 
        datetime_from = get_date(ans.xpath(ans_date_x)[0].attrib.get('datetime'))
        # grab ans username
        user_el = ans.xpath(ans_username_x)
        username = 'аноним'
        if (len(user_el) != 0):
            username = user_el[0].text

        a_list.append(Answer(p_id, username, datetime_from, content))

    np_link = tree.xpath(ans_next_page_x)
    if (len(np_link) != 0):
        an_page = host + np_link.attrib.get('href')[1:]
        process_answers(p_id, an_page)


def add_ans():
    spamwriter = csv.writer(q_filecsv, delimiter=',', quotechar='|', quoting=csv.QUOTE_ALL)
    for a in a_list:
        spamwriter.writerow(['', 'A', a.p_id, '',  # 'Id', 'Type', 'ParentIdInFile', 'ParentIdInSIte'
                             '', a.content, 'html', '', '',  # 'Title', 'Content', 'Format', 'CategoryId', 'CategoryUrl'
                             '', '', a.username, '', '',  # 'Tags', 'UserName', 'AnonymousName', 'Notify', 'ExtraValue',
                             a.datetime_from, '', ''])  # 'DateTimeFrom', 'DateTimeTo', 'Selected'


def add_cats():
    spamwriter = csv.writer(cat_filecsv, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
    for c_name, c_id in c_dict.items():
        spamwriter.writerow([c_id, c_name])


def get_tree(link):
    data = requests.get(link)  # bytes

    return html.fromstring(data.content.decode('utf-8'))


def get_date(date_str):
    # parse string
    date_obj = datetime.strptime(date_str, date_p)
    # set format for a date object
    return datetime.strftime(date_obj, date_f)


def get_tags(tags):
    t_str = ""
    leng = 4 if len(tags) > 4 else len(tags)
    for i in range(leng):
        t_str += tags[i].text + ", "

    return t_str[0:-2]


def get_id(c_name):
    return c_dict[c_name] if c_name in c_dict else create_cat(c_name)


def create_cat(c_name):
    global c_id
    c_id = c_id + 1
    c_dict[c_name] = c_id

    return c_id


# https://stackoverflow.com/questions/4624062/get-all-text-inside-a-tag-in-lxml
def stringify_children(node):
    parts = ([node.text] +
             list(chain(*([c.text, tostring(c, encoding=str), c.tail] for c in node.getchildren()))) +
             [node.tail])
    # filter removes possible Nones in texts and tails
    return ''.join(filter(None, parts))


if __name__ == '__main__':
    try:
        for i in range(0, last_page_num, 20):
            process_list_page(next_page + "?start=" + str(i))
            if ((i == 1000) or (i == last_page_num)):
                write_in_csv(i)
                # break
    finally:
        add_cats()
        cli_logger.warn("Added categories in " + cat_file)
        cat_filecsv.close()
        cli_logger.warn(cat_file + " is saved")
