#!/usr/bin/python
# -*- coding: utf-8 -*-

class Answer(object):
	def __init__(self, p_id, username, datetime_from, content):
		self.p_id = p_id
		self.username = username
		self.datetime_from = datetime_from
		self.content = content

	"""docstring for Answer"""
	# def __init__(self, arg):
	# 	super(Answer, self).__init__()
	# 	self.arg = arg
