#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import logging
import requests


class Host(object):

	LOGGER = logging.getLogger(f'{__name__}')

	def __init__(self, host: str) -> None:
		super(Host, self).__init__()

		self.host = host
		self.session = requests.Session()

	def __str__(self) -> str:
		return f'Host(host={self.host})'

	def GetHost(self) -> str:
		return self.host

