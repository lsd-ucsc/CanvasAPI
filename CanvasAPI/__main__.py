#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import argparse

from ._Meta import __version__


def main():
	parser = argparse.ArgumentParser(
		description='A Python package for Canvas API'
	)
	parser.add_argument(
		'--version',
		action='version',
		version=f'{__version__}',
	)
	args = parser.parse_args()


if __name__ == '__main__':
	main()

