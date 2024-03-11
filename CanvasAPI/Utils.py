#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import time

from typing import Callable


def PaginatingRequest(
	func: Callable,
	perpage: int = 50,
	pollInterval: float = 0.5,
) -> Callable:
	'''
	Decorator for paginating requests
	'''
	def wrapper(*args, **kwargs) -> list:
		'''
		Wrapper for paginating requests
		'''
		res = []
		page = 1
		while True:
			payload = func(*args, **kwargs, page=page, perPage=perpage, paginating=True)
			if len(payload) == 0:
				break
			res += payload
			page += 1
			time.sleep(pollInterval)

		return res

	return wrapper

