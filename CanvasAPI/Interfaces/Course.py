#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import json
import logging
import pandas

from typing import List, Union
from ..Auth.Auth import Auth
from ..Host import Host
from ..Utils import PaginatingRequest
from .Assignment import Assignment


class Roster(object):

	def __init__(
		self,
		payload: Union[List[dict], None] = None,
		cacheFilePath: Union[str, None] = None,
	) -> None:
		super(Roster, self).__init__()

		self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

		if payload is None and cacheFilePath is None:
			raise ValueError('Either payload or cacheFilePath must be provided.')

		if payload is not None and cacheFilePath is not None:
			self.payload = payload
			with open(cacheFilePath, 'w') as f:
				json.dump(payload, f, indent='\t')
		elif payload is not None:
			self.payload = payload
		else:
			with open(cacheFilePath, 'r') as f:
				self.payload = json.load(f)

		self.logger.debug(f'Loaded {len(self.payload)} users from the roster')

	def GetUserIdByEmail(self, email: str) -> Union[int, None]:
		'''
		Get the user ID by email
		'''
		userId = None

		for user in self.payload:
			if 'login_id' not in user:
				username = user['name']
				self.logger.warning(f'User {username} does not have login_id')
			elif user['login_id'].lower() == email.lower():
				if userId is not None:
					raise ValueError(f'Multiple users with the same email {email}')
				userId = user['id']

		if userId is None:
			raise ValueError(f'Cannot find user with email {email}')
		else:
			return userId

	def AddUserIdToDataFrame(self, df: pandas.DataFrame):
		'''
		Add the user ID to the DataFrame
		'''
		df['user_id'] = df.index.to_series().apply(self.GetUserIdByEmail)


class Course(object):

	def __init__(
		self,
		host:Host,
		auth: Auth,
		dashboard: 'Dashboard',
		cid: int,
	) -> None:
		super(Course, self).__init__()

		self.host = host
		self.auth = auth
		self.dashboard = dashboard

		self.id = cid

	def __str__(self) -> str:
		return f'Course(id={self.id})'

	def OpenAssignment(
		self,
		aid: Union[int, None]
	) -> 'Assignment':
		if aid is None:
			raise NotImplementedError('OpenAssignment with None is not implemented yet.')

		return Assignment(self.host, self.auth, self, aid)

	def GetRoster(
		self,
		searchTerm: Union[str, None] = None,
		sort: Union[str, None] = None,
		enrollmentType: Union[List[str], None] = None,
		include: Union[List[str], None] = None,
		userID: Union[str, None] = None,
		userIDs: Union[List[int], None] = None,
		enrollmentState: Union[List[str], None] = None,
		includeInactive: Union[bool, None] = None,
		perPage: Union[int, None] = None,
		page: Union[int, None] = None,
		paginating: bool = False,
	) -> 'Roster':
		'''
		Get the roster of the course
		Ref: https://canvas.instructure.com/doc/api/courses.html#method.courses.users
		'''
		path = f'/api/v1/courses/{self.id}/users'
		url = f'https://{self.host.GetHost()}{path}'

		headers = {}
		self.auth.AddAuth(headers)

		params = {}
		if searchTerm is not None:
			params['search_term'] = searchTerm
		if sort is not None:
			params['sort'] = sort
		if enrollmentType is not None:
			params['enrollment_type[]'] = enrollmentType
		if include is not None:
			params['include[]'] = include
		if userID is not None:
			params['user_id'] = userID
		if userIDs is not None:
			params['user_ids[]'] = userIDs
		if enrollmentState is not None:
			params['enrollment_state[]'] = enrollmentState
		if includeInactive is not None:
			params['include_inactive'] = includeInactive
		if perPage is not None:
			params['per_page'] = perPage
		if page is not None:
			params['page'] = page

		resp = self.host.session.get(url, headers=headers, params=params)

		resp.raise_for_status()

		jsonResp = resp.json()
		if paginating:
			return jsonResp
		else:
			return Roster(jsonResp)

	@PaginatingRequest
	def _GetRosterAll(self, *args, **kwargs) -> list:
		return self.GetRoster(*args, **kwargs)

	def GetRosterAll(self, *args, **kwargs) -> 'Roster':
		'''
		Automatically get all the roster of the course by paginating through the responses
		'''

		cacheFile = None
		if 'cacheFile' in kwargs and kwargs['cacheFile'] is not None:
			cacheFile = kwargs['cacheFile']
			try:
				roster = Roster(cacheFilePath=kwargs['cacheFile'])
				return roster
			except:
				pass

		if 'cacheFile' in kwargs:
			del kwargs['cacheFile']

		roster = Roster(
			payload=self._GetRosterAll(*args, **kwargs),
			cacheFilePath=cacheFile,
		)
		return roster
