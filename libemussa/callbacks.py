"""
Callback identifiers for libemussa

Being asynchronious, libemussa needs to know which methods to call when specific events
occur. This file contains the identifiers used when registering callbacks, along with
a short documentation for each one
"""


EMUSSA_CALLBACK_DISCONNECTED = 0
"""
Prototype:
def callback(EmussaSession emussa):
	///

Called on disconnection
"""


EMUSSA_CALLBACK_ISCONNECTING = 1
"""
Prototype:
def callback(EmussaSession emussa):
	///

Called before opening the socket to the YMSG server
"""


EMUSSA_CALLBACK_ISCONNECTED = 2
"""
Prototype:
def callback(EmussaSession emussa):
	///

Called when the socket connection was successfull.
"""


EMUSSA_CALLBACK_CONNECTIONFAILED = 3
"""
Prototype:
def callback(EmussaSession emussa, Exception e):
	///

Called when the connection failed. The given parameter is the exception generated on connection failure
"""



EMUSSA_CALLBACK_SIGNINERROR = 4
"""
Prototype:
def callback(EmussaSession emussa, int EMUSSA_ERROR_CODE):
	///

Called when the signing process failed (because of invalid credentials, locked account, et al).
See const.py for error codes.
"""


EMUSSA_CALLBACK_SELFCONTACT = 5
"""
Prototype:
def callback(EmussaSession emussa, PersonalInfo pi):
	///

Called when received personal info data; class PersonalInfo is defined in im.py
"""


EMUSSA_CALLBACK_GROUP_RECEIVED = 6
"""
Prototype:
def callback(EmussaSession emussa, Group group):
	///

Called when a new group is received; class BuddyList is defined in im.py.
"""


EMUSSA_CALLBACK_BUDDY_RECEIVED = 7
"""
Prototype:
def callback(EmussaSession emussa, Buddy buddy):
	///

Called when a new buddy is received; class Buddy is defined in im.py.
"""


EMUSSA_CALLBACK_BUDDY_UPDATE = 8
"""
Prototype:
def callback(EmussaSession emussa, Buddy b)
	///

Called when a buddy needs to be updated (e.g. changes its status); class Status is defined in im.py
"""


EMUSSA_CALLBACK_TYPING_NOTIFY = 9
"""
Prototype:
def callback(EmussaSession emussa, TypingNotify tn)
	///

Called when a typing notification is received; class TypingNotify is defined in im.py
"""


EMUSSA_CALLBACK_MESSAGE_IN = 10
"""
Prototype:
def callback(EmussaSession emussa, PersonalMessage msg)
	///

Called when an IM is received; class PersonalMessage is defined in im.py
"""


EMUSSA_CALLBACK_MESSAGE_SENT = 11
"""
Prototype:
def callback(EmussaSession emussa, PersonalMessage msg)
	///

Called after a message is sent; class PersonalMessage is defined in im.py
"""


EMUSSA_CALLBACK_STATUS_CHANGED = 12
"""
Prototype:
def callback(EmussaSession emussa, Status status)
	///

Called when self status (!!) is changed; class Status is defined in im.py
"""