import struct
from itertools import izip

from utils import YDict

YMSG_VER = chr(0x00) + chr(0x10) + chr(0x00) + chr(0x00)
YMSG_HEADER = 'YMSG'
YMSG_SEP = chr(0xc0) + chr(0x80)


class InvalidPacket(Exception):
    pass


class YPacketError(Exception):
	pass


class YPacket(object):
	def __init__(self, data = None):
		self._service = chr(0x00) + chr(0x00)
		self._length = chr(0x00) + chr(0x00)
		self._status = chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00)
		self._sid = chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00)
		self._keyvals = YDict()
		self._data = ''

		if data:
			self.populateFromData(data)

	# setter and getter for sid
	@property
	def sid(self):
		return self._sid

	@sid.setter
	def sid(self, value):
		self._sid = value

	# setter and getter for service
	@property
	def service(self):
		return struct.unpack('!H', self._service)[0]

	@service.setter
	def service(self, value):
		self._service = struct.pack('!H', value)


	# setter and getter for status
	@property
	def status(self):
		return struct.unpack('!I', self._status)[0]

	@status.setter
	def status(self, value):
		self._status = struct.pack('!I', value)


	# setter and getter for length
	@property
	def length(self):
		return struct.unpack('!H', self._length)[0]

	@length.setter
	def length(self, value):
		raise YPacketError("Packet length cannot be modified from outside")


	# setter and getter for data
	@property
	def data(self):
		return self._keyvals

	@data.setter
	def data(self, ydict):
		self._keyvals = ydict


	# misc functions
	def _packData(self):
		rawData = ''
		for key in self._keyvals:
			rawData += key + YMSG_SEP + self._keyvals[key] + YMSG_SEP
		return rawData

	def _unpackData(self, raw_data = None):
		ydict = YDict()
		if not raw_data:
			raw_data = self._data
		kv = raw_data.split(YMSG_SEP)
		i = iter(kv)
		l = list(izip(i, i))
		for key, val in l:
			ydict[key] = val
		return ydict

	def setHeader(self, headerdata):
		if not headerdata.startswith(YMSG_HEADER) or len(headerdata) < 20:
			raise InvalidPacket("Invalid header")

		self._service = headerdata[10:12]
		self._length = headerdata[8:10]
		self._status = headerdata[12:16]
		self._sid = headerdata[16:20]

	def setData(self, rawdata):
		self._data = rawdata
		self._keyvals = self._unpackData()

	def populateFromData(self, data):
		self.setHeader(header)
		self.setData(data[20:])

	def __str__(self):
		self._data = self._packData()
		self._length = struct.pack('!H', len(self._data))
		return YMSG_HEADER + YMSG_VER + self._length + self._service + self._status + self._sid + self._data

	def __repr__(self):
		return "<Packet Type={0}, Length={1}b, Status={2}, Data={3}>".format(hex(self.service), self.length, self._status, self._keyvals)
