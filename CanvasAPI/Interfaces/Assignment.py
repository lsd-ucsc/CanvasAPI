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

from typing import List, Tuple, Union
from ..Auth.Auth import Auth
from ..Host import Host
from ..Utils import PaginatingRequest


class Submissions(object):

	def __init__(
		self,
		payload: Union[List[dict], None] = None,
		cacheFilePath: Union[str, None] = None,
	) -> None:
		super(Submissions, self).__init__()

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

		self.logger.debug(f'Loaded {len(self.payload)} submissions')

	def GetScoreByUserId(self, uid: int) -> Tuple[bool, float]:
		'''
		Get the score by user ID
		'''
		found = False
		score = None

		for submission in self.payload:
			if submission['user_id'] == uid:
				if found:
					raise ValueError(f'Multiple submissions found for user {uid}')
				found = True
				score = submission['score']

		return found, score


class Assignment(object):

	def __init__(
		self,
		host:Host,
		auth: Auth,
		course: 'Course',
		aid: int,
	) -> None:
		super(Assignment, self).__init__()

		self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

		self.host = host
		self.auth = auth
		self.course = course

		self.id = aid

	def GetSubmissions(
		self,
		include: Union[List[str], None] = None,
		grouped: bool = False,
		perPage: Union[int, None] = None,
		page: Union[int, None] = None,
		paginating: bool = False,
	) -> list:
		'''
		Get the submissions of the assignment
		Ref: https://canvas.instructure.com/doc/api/submissions.html#method.submissions_api.index
		'''
		path = f'/api/v1/courses/{self.course.id}/assignments/{self.id}/submissions'
		url = f'https://{self.host.GetHost()}{path}'

		headers = {}
		self.auth.AddAuth(headers)

		params = {}
		if include is not None:
			params['include[]'] = include
		if grouped:
			params['grouped'] = True
		if perPage is not None:
			params['per_page'] = perPage
		if page is not None:
			params['page'] = page

		resp = self.host.session.get(url, headers=headers, params=params)

		resp.raise_for_status()
		if paginating:
			return resp.json()
		else:
			return Submissions(payload=resp.json())

	@PaginatingRequest
	def _GetAllSubmissions(self, *args, **kwargs) -> list:
		'''
		Wrapper for paginating requests
		'''
		return self.GetSubmissions(*args, **kwargs)

	def GetAllSubmissions(self, *args, **kwargs) -> Submissions:
		'''
		Get all submissions of the assignment
		'''
		cacheFile = None
		if 'cacheFile' in kwargs and kwargs['cacheFile'] is not None:
			cacheFile = kwargs['cacheFile']
			try:
				subs = Submissions(cacheFilePath=kwargs['cacheFile'])
				return subs
			except:
				pass

		if 'cacheFile' in kwargs:
			del kwargs['cacheFile']

		subs = Submissions(
			payload=self._GetAllSubmissions(*args, **kwargs),
			cacheFilePath=cacheFile,
		)
		return subs

	def GradeSubmission(
		self,
		sid: int,
		grade: Union[str, None] = None,
		commentStr: Union[str, None] = None,
		attempt: Union[int, None] = None,
		visibility: Union[str, None] = None,
		excuse: Union[bool, None] = None,
		latePolicyStatus: Union[str, None] = None,
		secondsLateOverride: Union[int, None] = None,
	) -> None:
		'''
		Grade a submission
		Ref: https://canvas.instructure.com/doc/api/submissions.html#method.submissions_api.update
		'''
		path = f'/api/v1/courses/{self.course.id}/assignments/{self.id}/submissions/{sid}'
		url = f'https://{self.host.GetHost()}{path}'

		headers = {}
		self.auth.AddAuth(headers)

		params = {}
		if grade is not None:
			params['submission[posted_grade]'] = grade
		if commentStr is not None:
			params['comment[text_comment]'] = commentStr
		if attempt is not None:
			params['comment[attempt]'] = attempt
		if visibility is not None:
			params['include[visibility]'] = visibility
		if excuse is not None:
			params['submission[excuse]'] = excuse
		if latePolicyStatus is not None:
			params['submission[late_policy_status]'] = latePolicyStatus
		if secondsLateOverride is not None:
			params['submission[seconds_late_override]'] = secondsLateOverride

		resp = self.host.session.put(url, headers=headers, params=params)

		resp.raise_for_status()

	def SyncGradesByDataFrame(
		self,
		grades: pandas.DataFrame,
		scoreCol: str,
		submissionCache: Union[str, None] = None,
		dryRun: Union[int, None] = None,
	) -> None:
		'''
		Sync grades using a given pandas DataFrame
		'''
		submissions = self.GetAllSubmissions(cacheFile=submissionCache)

		i = 0
		total = len(grades)
		for _, row in grades.iterrows():
			progPercent = (i / total) * 100

			userId = row['user_id']
			oriFound, oriScore = submissions.GetScoreByUserId(userId)
			newScore = row[scoreCol]

			if not oriFound:
				self.logger.info(
					f'Progress {progPercent:.2f}%: '
					f'No submission found for user {userId}, new score {newScore}'
				)
				if dryRun is None or i < dryRun:
					self.GradeSubmission(sid=userId, grade=newScore)
				else:
					self.logger.debug('Dry run, no submission is updated')
			elif oriScore != newScore:
				self.logger.info(
					f'Progress {progPercent:.2f}%: '
					f'Updating submission for user {userId}, from {oriScore} to {newScore}'
				)
				if dryRun is None or i < dryRun:
					self.GradeSubmission(sid=userId, grade=newScore)
				else:
					self.logger.debug('Dry run, no submission is updated')
			else:
				self.logger.info(
					f'Progress {progPercent:.2f}%: '
					f'No change for user {userId}, score matched {oriScore}=={newScore}'
				)

			i += 1

