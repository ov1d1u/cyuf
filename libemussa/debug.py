# Simple debugger for libEmussa
# Levels:
# 0 - disable
# 1 - only errors
# 2 - errors and warning
# 3 - all
import sys, time, os

class bcolors:
    INFO = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'

class Debugger:
	def __init__(self):
		self._level = 3
		self.fh = sys.stdout

	# setter and getter for level
	@property
	def level(self):
		return self._level

	@level.setter
	def level(self, lvl):
		print 'Debug level set to {0}'.format(lvl)
		self._level = lvl
		self.info('Debug level set to {0}'.format(lvl))

	def info(self, message):
		if self._level >= 3:
			line = message
			if self.fh == sys.stdout:
				line = '{0}[INFO]{1} {2}{3}'.format(bcolors.INFO, bcolors.ENDC, message, os.linesep)
			else:
				line = '[{0}] I: {1}{2}'.format(time.ctime(), message, os.linesep)

			self.fh.write(line)

	def warning(self, message):
		if self._level >= 2:
			line = message
			if self.fh == sys.stdout:
				line = '{0}[WARNING]{1} {2}{3}'.format(bcolors.WARNING, bcolors.ENDC, message, os.linesep)
			else:
				line = '[{0}] W: {1}{2}'.format(time.ctime(), message, os.linesep)

			self.fh.write(line)

	def error(self, message):
		if self._level >= 1:
			line = message
			if self.fh == sys.stdout:
				line = '{0}[ERROR]{1} {2}{3}'.format(bcolors.ERROR, bcolors.ENDC, message, os.linesep)
			else:
				line = '[{0}] E: {1}{2}'.format(time.ctime(), message, os.linesep)

			self.fh.write(line)