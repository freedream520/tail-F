#!/usr/bin/env python
# encoding: utf-8


import os
import sys

import pyinotify


DIRMASK = pyinotify.IN_MODIFY \
    | pyinotify.IN_ATTRIB \
    | pyinotify.IN_MOVE_SELF \
    | pyinotify.IN_CREATE


class Handler(pyinotify.ProcessEvent):

    def __init__(self, filename):
        self._fh = None
        self._path = filename

        super(Handler, self).__init__()

    def my_init(self):
        try:
            self._fh = open(self._path, 'r')
        except IOError, e:
            sys.stderr.write('open file failed, %s' % e)
        else:
            self._fh.seek(0, 2)

    def process_IN_CREATE(self, event):
        path = self._path

        if path in os.path.join(event.path, event.name):
            if hasattr(self, 'fh'):
                self._fh.close()

            try:
                self._fh = open(self._path, 'r')
            except IOError, e:
                sys.stderr.write('open file failed, %s' % e)
            else:
                self._fh.seek(0, 2)

                for r in self._fh.readlines():
                    sys.stdout.write(r)

    def process_IN_MODIFY(self, event):
        path = self._path

        if path not in os.path.join(event.path, event.name):
            return

        if not self._fh.closed:
            for r in self._fh.readlines():
                sys.stdout.write(r)

    def process_IN_MOVE_SELF(self, event):
        path = self._path

        if path in os.path.join(event.path, event.name):
            sys.stderr.write('monitor file move')

    def process_IN_ATTRIB(self, event):
        pass


class Tailer(object):

    def __init__(self, filename):
        super(Tailer, self).__init__()
        self._path = filename
        self._notifier = None

        self._init()

    def __del__(self):
        self._notifier.stop()

    def _init(self):
        path = self._path

        index = path.rfind('/')
        wm = pyinotify.WatchManager()
        wm.add_watch(path[:index], DIRMASK)

        handler = Handler(path)
        self._notifier = pyinotify.Notifier(wm, handler)

    def run(self):
        while True:
            self._notifier.process_events()

            if self._notifier.check_events():
                self._notifier.read_events()


if __name__ == '__main__':
    if len(sys.argv[1:]) != 1:
        print 'Usage: python tail.py </path/to/filename>'
        sys.exit(0)

    path = sys.argv[1]
    Tailer(path).run()
