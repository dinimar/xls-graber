#!/usr/bin/python
# -*- coding: utf-8 -*-

class Question(object):
	def __init__(self, q_id, title, tags, username, datetime_from, content, cat_id):
		self.q_id = q_id
		self.tags = tags
		self.title = title
		self.username = username
		self.datetime_from = datetime_from
		self.content = content
		self.cat_id = cat_id

	"""docstring for Question"""
	# def __init__(self, arg):
	# 	super(Question, self).__init__()
	# 	self.arg = arg
		