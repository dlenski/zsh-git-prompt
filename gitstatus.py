#!/usr/bin/env python
from __future__ import print_function

# change this symbol to whatever you prefer
prehash = ':'

from subprocess import Popen, PIPE

import sys

gitstatus = Popen(['git', 'status', '--porcelain=v2', '-b'], stdout=PIPE, stderr=PIPE, universal_newlines=True)
stdout, error = gitstatus.communicate()

if gitstatus.returncode != 0 or 'fatal' in error:
	sys.exit(0)

stdout = stdout.splitlines()

in_header = True
header = {}
changed_files = set()
staged_files = set()
untracked_files = set()
conflict_files = set()

for line in stdout:
	if not line.startswith('#'):
		in_header = False
	if in_header:
		_, k, v = line.split(maxsplit=2)
		header[k] = v
	elif line.startswith(('1', '2')):
		if line[0] == '1':    # "normal" change
			bits = line.split(maxsplit=8)
			st, path = bits[1], bits[8]
		elif line[0] == '2':  # rename/move
			bits = line.split(maxsplit=9)
			st, (path, new_path) = bits[1], bits[9].split('\t', 1)

		if st[0] != '.':
			staged_files.add(path)
		if st[1] != '.':
			changed_files.add(path)
	elif line.startswith('u'):    # unmerged(conflict)
		bits = line.split(maxsplit=10)
		path = bits[10]
		conflict_files.add(path)
	elif line.startswith('?'):    # untracked file
		bits = line.split(maxsplit=1)
		path = bits[1]
		untracked_files.add(path)

branch = header.get('branch.head')
if branch in (None, '(detached)'):
	branch = prehash + header.get('branch.oid')[:8]
ahead, behind = (abs(int(x)) for x in header.get('branch.ab', '0 0').split(maxsplit=1))

print('%s %s %s %d %d %d %d' % (
	branch,
	ahead,
	behind,
	len(staged_files),
	len(conflict_files),
	len(changed_files),
	len(untracked_files),
	))
