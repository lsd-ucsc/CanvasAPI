#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


from typing import Union
from ..Auth.Auth import Auth
from ..Host import Host
from .Course import Course


class Dashboard(object):

	@classmethod
	def GetSelfProfile(
		cls,
		host: Host,
		auth: Auth,
	) -> 'Dashboard':
		"""
		Get the profile of the current user
		"""
		path = '/api/v1/users/self'
		url = f'https://{host.GetHost()}{path}'

		headers = {}
		auth.AddAuth(headers)

		resp = host.session.get(url, headers=headers)

		resp.raise_for_status()
		return resp.json()

	def __init__(
		self,
		host:Host,
		auth: Auth,
		uid: Union[int, None] = None,
	) -> None:
		super(Dashboard, self).__init__()

		self.host = host
		self.auth = auth

		if uid is None:
			profile = self.GetSelfProfile(host, auth)
			self.uid = profile['id']
		else:
			self.uid = uid

	def __str__(self) -> str:
		return f'Dashboard(uid={self.uid})'

	def OpenCourse(self, cid: Union[int, None]) -> Course:
		if cid is None:
			raise NotImplementedError('OpenCourse() with None is not implemented yet')

		return Course(self.host, self.auth, self, cid)

