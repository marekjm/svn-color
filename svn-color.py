#!/usr/bin/env python3

"""
 Author: Saophalkun Ponlu (http://phalkunz.com)
 Contact: phalkunz@gmail.com
 Date: May 23, 2009
 Modified: June 15, 2009

 Additional modifications:
 Author: Phil Christensen (http://bubblehouse.org)
 Contact: phil@bubblehouse.org
 Date: February 22, 2010

 Additional modifications:
 Author: Marek Marecki (http://marecki.me)
 Contact: marekjm@ozro.pw
 Date: December 15, 2017
"""

import os, sys, subprocess, re

colorizedSubcommands = (
    'status',
    'stat',
    'st',
    'add',
    'remove',
    'diff',
    'di',
    'log',
    'update',
    'up',
)


class Matcher:
    def match(self, line):
        if hasattr(self, 'starts_with'):
            return line.startswith(self.starts_with)
        if hasattr(self, 'starts_with_regex'):
            return re.match(self.starts_with_regex, line) is not None
        return False

    def apply_color(self, color, text):
        return ''.join(("\033[", color, 'm', text, "\033[m"))

    def colorise(self, line):
        if hasattr(self, 'color'):
            return self.apply_color(self.color, line)
        return line

class AtRevision(Matcher):
    starts_with = 'At revision'

    def colorise(self, line):
        matched = re.match(re.compile('^At revision (\d+)\.$'), line)
        revision = self.apply_color('38;5;255;1', matched.group(1))
        return 'At revision {}.\n'.format(revision)

class UpdatedToRevision(Matcher):
    starts_with = 'Updated to revision'

    def colorise(self, line):
        matched = re.match(re.compile('^Updated to revision (\d+)\.$'), line)
        revision = self.apply_color('38;5;255;1', matched.group(1))
        return 'Updated to revision {}.\n'.format(revision)

class CommitedRevision(Matcher):
    starts_with = 'Commited revision'

    def colorise(self, line):
        matched = re.match(re.compile('^Commited revision (\d+)\.$'), line)
        revision = self.apply_color('38;5;255;1', matched.group(1))
        return 'Commited revision {}.\n'.format(revision)

class StatusModified(Matcher):
    starts_with_regex = re.compile(r'^M\b')
    color = '32'

class LogModified(Matcher):
    starts_with = '   M'

    def colorise(self, line):
        return self.apply_color('38;5;34;1', line[:4]) + self.apply_color('97', line[4:])

class LogIndex(Matcher):
    starts_with = 'Index: '

    def colorise(self, line):
        return self.apply_color('37;1', line[:len(self.starts_with)]) + self.apply_color('97', line[len(self.starts_with):])

class Untracked(Matcher):
    starts_with = '?'
    color = '37'

class StatusAdded(Matcher):
    starts_with_regex = re.compile(r'^A\b')
    color = '32'

class LogAdded(Matcher):
    starts_with = '   A'

    def colorise(self, line):
        return self.apply_color('38;5;82;1', line[:4]) + self.apply_color('97', line[4:])

class StatusX(Matcher):
    starts_with_regex = re.compile(r'^X\b')
    color = '31'

class StatusC(Matcher):
    starts_with_regex = re.compile(r'^C\b')
    color = '30;41'

class DiffRemoved(Matcher):
    starts_with = '-'
    color = '31'

    def match(self, line):
        return line.startswith('-') and not line.startswith('-----')

class StatusD(Matcher):
    starts_with_regex = re.compile(r'^D\b')
    color = '31;1'  # bold red

class StatusU(Matcher):
    starts_with_regex = re.compile(r'^U\b')
    color = '32;1'  # bold green

class StatusG(Matcher):
    starts_with_regex = re.compile(r'^G\b')
    color = '32;1'  # bold green

class DiffAdded(Matcher):
    starts_with = '+'
    color = '32'

class DiffMarker(Matcher):
    starts_with = '@@'
    color = '38;5;75'

class RevisionHeader(Matcher):
    matching_regex = re.compile(r'^(r\d+) \| (.*?) \| (.*?) \| (\d+ lines?)$')
    color = '38;5;202'

    def match(self, line):
        return re.match(self.matching_regex, line) is not None

    def colorise(self, line):
        matched = re.match(self.matching_regex, line)
        revision = self.apply_color('38;5;255;1', matched.group(1))
        user = self.apply_color('38;5;220', matched.group(2))
        date_and_time = matched.group(3)
        lines_changed = self.apply_color('38;5;46;1', matched.group(4))
        return ' | '.join((revision, user, date_and_time, lines_changed)) + '\n'



statusColors = (
    AtRevision(),
    UpdatedToRevision(),
    StatusModified(),
    LogModified(),
    LogIndex(),
    Untracked(),
    StatusAdded(),
    LogAdded(),
    StatusX(),
    StatusC(),
    DiffRemoved(),
    StatusD(),
    StatusU(),
    StatusG(),
    DiffAdded(),
    DiffMarker(),
    RevisionHeader(),
)

def colorize(line):
    for each in statusColors:
        if each.match(line):
            return each.colorise(line)
    else:
        return line

if __name__ == '__main__':
    command = sys.argv
    command[0] = '/usr/bin/svn'

    if len(command) > 1:
        subcommand = (command[1], '')[len(command) < 2]
    else:
        subcommand = ''
    if subcommand in colorizedSubcommands and (sys.stdout.isatty() or os.environ.get('SVN_COLOR', 'always')):
        task = subprocess.Popen(command, stdout=subprocess.PIPE)
        while True:
            line = task.stdout.readline().decode('utf-8')
            if not line:
                break
            sys.stdout.write(colorize(line))
            sys.stdout.flush()
    else:
        task = subprocess.Popen(command)
    task.communicate()
    sys.exit(task.returncode)
