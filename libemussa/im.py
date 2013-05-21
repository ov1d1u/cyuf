class PersonalInfo:
	def __init__(self):
		self.yahoo_id = ''		# our Yahoo! ID
		self.name = ''			# Real name
		self.surname = ''		# Real surname
		self.country = ''		# Country ID

class Buddy:
	def __init__(self):
		self.yahoo_id = ''		# buddy's Yahoo! ID
		self.nickname = ''		# buddy's nickname
		self.status   = None	# buddy Status
		self.ignored  = False	# buddy is on ignore list

	def __repr__(self):
		return '<Buddy: "{0}">'.format(self.yahoo_id)

class Group:
	def __init__(self):
		self.name = ''			# group name
		self.buddies = []		# a list of Buddy

	def __repr__(self):
		return '<Group: "{0}", count: {1}>'.format(self.name, len(self.buddies))


class Status:
	def __init__(self):
		self.online = False
		self.code = 0x00
		self.message = ''
		self.idle_time = 0


class TypingNotify:
	def __init__(self):
		self.sender = ''		# buddy's Yahoo! ID
		self.receiver = ''		# usually our ID
		self.status = 0 		# 0 - stopped; 1 - started


class PersonalMessage:
	def __init__(self):
		self.sender = ''
		self.receiver = ''
		self.timestamp = ''
		self.message = ''