#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


from . import Auth


class Token(Auth.Auth):

	@classmethod
	def FromFile(cls, path: str) -> 'Token':
		with open(path, 'r') as f:
			token = f.read().strip()
		return cls(token)

	def __init__(self, token: str) -> None:
		super(Token, self).__init__()

		self.token = token

	def AddAuth(self, headers: dict) -> None:
		headers['Authorization'] = f'Bearer {self.token}'

