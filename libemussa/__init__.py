import socket, urllib, threading, time
import Queue

from ypacket import YPacket, InvalidPacket
from debug import Debugger
from callbacks import *
import const, im, utils

HOST = 'scsa.msg.yahoo.com'
PORT = 5050
CLIENT_BUILD_ID = '4194239'
CLIENT_VERSION = '9.0.0.2162'
KEEP_ALIVE_TIMEOUT = 30

# init the debugger
debug = Debugger()
queue = Queue.Queue()

class EmussaException(Exception):
    def __init__(self, message, value = const.EMUSSA_ERROR_UNDEFINED):
        debug.error(message)
        self.message = message
        self.value = value

    def __str__(self):
        return self.message

class EmussaSession:
    def __init__(self):
        self.username = ''
        self.password = ''
        self.cbs = {}
        self.session_id = "\x00\x00\x00\x00"
        self.is_invisible = False
        self.is_connected = False
        self.last_keepalive = 0
        self.y_cookie = self.t_cookie = ''
        self.debug = debug
        self.debug.info('Hi, libemussa here!')

    def _callback(self, callback_id, *args):
        if self.cbs.has_key(callback_id):
            for func in self.cbs[callback_id]:
                func(self, *args)

    def _get_status_type(self):
        if self.is_invisible:
            return const.YAHOO_STATUS_INVISIBLE
        else:
            return const.YAHOO_STATUS_AVAILABLE

    def _connect(self, server, port):
        try:
            debug.info('Connecting to {0}:{1}'.format(server, port))
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((server, port))
            debug.info('Connection successful')
            self.is_connected = True
            threading.Thread(target=self._listener).start()
        except Exception, e:
            self.is_connected = False
            debug.error('Connection failed')
            self._callback(EMUSSA_CALLBACK_CONNECTIONFAILED, e)
            self._disconnect()

    def _disconnect(self):
        if self.is_connected:
            self.is_connected = False
            self.s.shutdown(socket.SHUT_WR)
            queue.put(None) # put this in queue to force stopping the sender thread

    def _listener(self):
        if not self.is_connected:
            e = EmussaException("Cannot listen to an uninitialized socket", const.EMUSSA_ERROR_NOSOCKET)
            self._callback(EMUSSA_CALLBACK_CONNECTIONFAILED, e)
            self._disconnect()
            raise e

        debug.info('Starting the socket listener')
        while self.is_connected:
            header = body = ''
            try:
                header = self.s.recv(20)
                y = YPacket()
                y.setHeader(header)
                while len(body) < y.length:
                    body += self.s.recv(y.length - len(body))
                y.setData(body)
                self._process_packet(y)
            except InvalidPacket:
                debug.warning('Invalid packet received, skipping')
            #except:
            #    debug.warning('Error while reading data packet')
        debug.info('Listener thread ended.')
        self.is_connected = False

    def _sender(self):
        if not self.is_connected:
            EmussaException("Cannot write to an uninitialized socket", const.EMUSSA_ERROR_NOSOCKET)

        debug.info('Starting the socket writer')
        while self.is_connected:
            ypack = queue.get(True)
            if not ypack:
                continue
            ypack.sid = self.session_id
            debug.info('Sending packet of type {0}'.format(hex(ypack.service)))
            self.s.sendall(str(ypack))
            debug.info('Sent {0} bytes'.format(len(str(ypack))))
            queue.task_done()
        debug.info('Sender thread ended.')

    def _send(self, y):
        if not self.is_connected:
            self._connect(HOST, PORT)
            threading.Thread(target=self._sender).start()
        queue.put(y)

    def _keepalive(self):
        self.last_keepalive = time.time()
        while self.is_connected:
            time.sleep(1)
            if self.last_keepalive + KEEP_ALIVE_TIMEOUT < time.time() and self.is_connected:
                y = YPacket()
                y.service = const.YAHOO_SERVICE_KEEPALIVE
                y.status = self._get_status_type()
                y.data['0'] = self.username
                self._send(y)
                self.last_keepalive = time.time()

    def _process_packet(self, y):
        if y.sid != "\x00\x00\x00\x00":
            debug.info('Setting session id')
            self.session_id = y.sid

        if y.service == const.YAHOO_SERVICE_AUTH:
            challenge = y.data['94']
            self._auth_response(challenge)
        
        elif y.service == const.YAHOO_SERVICE_LIST:
            self._received_own_contact(y.data)
        
        elif y.service == const.YAHOO_SERVICE_LIST_15:
            self._received_buddylist(y.data)

        elif y.service == const.YAHOO_SERVICE_STATUS_15:
            self._buddy_online(y.data)

        elif y.service == const.YAHOO_SERVICE_LOGOFF:
            self._buddy_offline(y.data)

        elif y.service == const.YAHOO_SERVICE_TYPING:
            self._typing(y.data)

        elif y.service == const.YAHOO_SERVICE_MESSAGE:
            self._message_received(y.data)

        elif y.service == const.YAHOO_SERVICE_Y6_STATUS_UPDATE:
            self._buddy_changed_status(y.data)

        else:
            debug.warning('Unknown packet of type {0}, skipping'.format(hex(y.service)))

    def _request_auth(self):
        y = YPacket()
        y.service = const.YAHOO_SERVICE_AUTH
        y.status = self._get_status_type()
        y.data['1'] = self.username
        self._send(y)

    def _auth_response(self, challenge):
        debug.info('Requesting token')
        token_url = const.YAHOO_TOKEN_URL.format(self.username, self.password, urllib.quote(challenge))
        lines = urllib.urlopen(token_url).read().split('\r\n')
        errcode = lines[0]
        if errcode == '0':
            debug.info('Got token')
        elif errcode == '100':
            e = EmussaException("Missing required field (username or password).", const.EMUSSA_ERROR_MISSING_REQUIRED_FIELD)
            self._callback(EMUSSA_CALLBACK_SIGNINERROR, e)
            self._disconnect()
            raise e
        elif errcode == '1013':
            e = EmussaException("Username contains @yahoo.com or similar but should not; strip this information.", const.EMUSSA_ERROR_CONTAINS_AT_YAHOO_COM)
            self._callback(EMUSSA_CALLBACK_SIGNINERROR, e)
            self._disconnect()
            raise e
        elif errcode == '1212':
            e = EmussaException("The username or password is incorrect.", const.EMUSSA_ERROR_INCORRECT_CREDENTIALS)
            self._callback(EMUSSA_CALLBACK_SIGNINERROR, e)
            self._disconnect()
            raise e
        elif errcode == '1213' or errcode == '1236':
            e = EmussaException("The account is locked because of too many login attempts.", const.EMUSSA_ERROR_ACC_LOCKED)
            self._callback(EMUSSA_CALLBACK_SIGNINERROR, e)
            self._disconnect()
            raise e
        elif errcode == '1214':
            e = EmussaException("Security lock requiring the use of a CAPTCHA.", const.EMUSSA_ERROR_NEED_CAPTCHA)
            self._callback(EMUSSA_CALLBACK_SIGNINERROR, e)
            self._disconnect()
            raise e
        elif errcode == '1218':
            e = EmussaException("The account has been deactivated by Yahoo.", const.EMUSSA_ERROR_ACC_DEACTIVATED)
            self._callback(EMUSSA_CALLBACK_SIGNINERROR, e)
            self._disconnect()
            raise e
        elif errcode == '1235':
            e = EmussaException("The username does not exist.", const.EMUSSA_ERROR_ACC_NOT_EXISTS)
            self._callback(EMUSSA_CALLBACK_SIGNINERROR, e)
            self._disconnect()
            raise e
        else:
            e = EmussaException("Login error: {0}".format(errcode), const.EMUSSA_ERROR_UNDEFINED)
            self._callback(EMUSSA_CALLBACK_SIGNINERROR, e)
            self._disconnect()
            raise e

        token_string = ''
        for line in lines[1:len(lines)]:
                key, value = line.split('=', 1)
                if key == 'ymsgr':
                    token_string = value

        if not len(token_string):
            e = EmussaException("Invalid token received.", const.EMUSSA_ERROR_INVALID_TOKEN)
            self._callback(EMUSSA_CALLBACK_SIGNINERROR, e)
            self._disconnect()
            raise e

        debug.info('Requesting cookies')
        login_url = const.YAHOO_LOGIN_URL.format(token_string)
        lines = urllib.urlopen(login_url).read().split('\r\n')
        errcode == lines[0]
        if errcode != '0':
            e = EmussaException("Token rejected by server.", const.EMUSSA_ERROR_INVALID_TOKEN)
            self._callback(EMUSSA_CALLBACK_SIGNINERROR, e)
            self._disconnect()
            raise e
        debug.info('Got cookies')

        crumb = ''
        for line in lines[1:len(lines)]:
            if not '=' in line:
                continue

            key, value = line.split('=', 1)
            if key == 'crumb':
                crumb = value
            if key == 'Y':
                self.y_cookie = value
            if key == 'T':
                self.t_cookie = value

        hash = utils.yahoo_generate_hash(crumb + challenge)
        y = YPacket()
        y.service = const.YAHOO_SERVICE_AUTHRESP
        y.status = self._get_status_type()
        keyvals = {
        '0'   : self.username,
        '1'   : self.username,
        '277' : self.y_cookie,
        '278' : self.t_cookie,
        '307' : hash,
        '244' : CLIENT_BUILD_ID,
        '2'   : '1',
        '59'  : '',
        '98'  : 'us',
        '135' : CLIENT_VERSION
        }
        y.data.import_dictionary(keyvals)
        self._send(y)
        self._callback(EMUSSA_CALLBACK_ISCONNECTED)

    def _received_own_contact(self, data):
        debug.info('Received self details')
        pi = im.PersonalInfo()
        pi.yahoo_id = data['3']
        pi.name = data['216']
        pi.surname = data['254']
        pi.country = data['470']
        self._callback(EMUSSA_CALLBACK_SELFCONTACT, pi)

        debug.info('Starting keepalive thread')
        threading.Thread(target=self._keepalive).start()

    def _received_buddylist(self, data):
        debug.info('Received buddylist')

        mode = ''
        for key in data:
            if key == '300':
                mode = data[key]

            if key == '65':
                group = im.Group()
                group.name = data[key]
                self._callback(EMUSSA_CALLBACK_GROUP_RECEIVED, group)

            if key == '7':
                buddy = im.Buddy()
                buddy.yahoo_id = data[key]
                buddy.status = im.Status()
                if mode == '320':
                    buddy.ignored = True
                self._callback(EMUSSA_CALLBACK_BUDDY_RECEIVED, buddy)

        data.reset()

    def _buddies_from_data(self, data):
        buddies = []

        buddy = None
        for key in data:
            if key == '7':
                buddy = im.Buddy()
                buddy.yahoo_id = data[key]
                buddy.status = im.Status()
                buddies.append(buddy)
            if key == '10':
                if buddy:
                    buddy.status.online = True
            if key == '19':
                if buddy:
                    buddy.status.message = data[key]
            if key == '47':
                if data[key] == '0':
                    buddy.status.code = const.YAHOO_STATUS_AVAILABLE
                elif data[key] == '1':
                    buddy.status.code = const.YAHOO_STATUS_BUSY
                elif data[key] == '2':
                    buddy.status.code = const.YAHOO_STATUS_BRB
            if key == '137':
                if buddy:
                    buddy.status.idle_time = data[key]
        return buddies

    def _buddy_online(self, data):
        debug.info('Set buddy online')
        updated_buddies = self._buddies_from_data(data)

        for ub in updated_buddies:
            self._callback(EMUSSA_CALLBACK_BUDDY_UPDATE, ub)

    def _buddy_offline(self, data):
        debug.info('Set buddy offline')
        buddy = im.Buddy()
        buddy.yahoo_id = data['7']
        buddy.status = im.Status()
        buddy.status.online = False
        self._callback(EMUSSA_CALLBACK_BUDDY_UPDATE, buddy)

    def _buddy_changed_status(self, data):
        debug.info('Update buddy status')
        buddy = self._buddies_from_data(data)[0]
        self._callback(EMUSSA_CALLBACK_BUDDY_UPDATE, buddy)

    def _typing(self, data):
        typing = im.TypingNotify()
        typing.sender = data['4']
        typing.receiver = data['5']
        typing.status = int(data['13'])
        if typing.status:
            debug.info('Typing: {0}'.format(typing.sender))
        else:
            debug.info('End typing: {0}'.format(typing.sender))
        self._callback(EMUSSA_CALLBACK_TYPING_NOTIFY, typing)

    def _message_received(self, data):
        debug.info('New personal IM')
        msg = im.PersonalMessage()
        msg.sender = data['4']
        msg.receiver = data['5']
        #msg.timestamp = data['15']
        msg.message = data['14']
        self._callback(EMUSSA_CALLBACK_MESSAGE_IN, msg)

    def _send_message(self, msg):
        y = YPacket()
        y.service = const.YAHOO_SERVICE_MESSAGE
        y.status = self._get_status_type()
        keyvals = {
        '1'   : self.username,
        '5'   : msg.receiver,
        '14'  : msg.message
        }
        y.data.import_dictionary(keyvals)
        self._send(y)
        self._callback(EMUSSA_CALLBACK_MESSAGE_SENT)

    def _set_status(self, status):
        is_not_available = '1'
        if status.code == const.YAHOO_STATUS_AVAILABLE:
            is_not_available = '0'
        y = YPacket()
        y.service = const.YAHOO_SERVICE_Y6_STATUS_UPDATE
        y.status = self._get_status_type()
        y.data['10'] = str(status.code)
        y.data['19'] = status.message
        y.data['47'] = is_not_available

        if status.message:
            # fix status type if the client did it wrong
            y.data.replace_key('10', 0, str(const.YAHOO_STATUS_CUSTOM))
            y.data['97'] = '1'  # this means UTF8, I guess
        self._send(y)
        self._callback(EMUSSA_CALLBACK_STATUS_CHANGED, status)

    def _toggle_visible(self, invisible = False):
        y = YPacket()
        y.service = const.YAHOO_SERVICE_Y6_VISIBLE_TOGGLE
        y.status = self._get_status_type()
        if invisible:
            y.data['13'] = '2'
        else:
            y.data['13'] = '1'
        self._send(y)            

    # "public" methods
    def register_callback(self, callback_id, function):
        if self.cbs.has_key(callback_id):
            self.cbs[callback_id].append(function)
        else:
            self.cbs[callback_id] = [function]

    def unregister_callback(self, callback_id, function):
        if self.cbs.has_key(callback_id):
            if function in self.cbs[callback_id]:
                self.cbs[callback_id].pop(self.cbs[callback_id].index(function))

    def disconnect(self):
        self._disconnect()
        self._callback(EMUSSA_CALLBACK_DISCONNECTED)

    def signin(self, username, password):
        debug.info('Starting authentication')
        self.username = username
        self.password = password
        self._callback(EMUSSA_CALLBACK_ISCONNECTING)
        self._request_auth()

    def send_message(self, to, message):
        debug.info('Sending IM to {0}'.format(to))
        msg = im.PersonalMessage()
        msg.sender = self.username,
        msg.receiver = to
        msg.timestamp = 0
        msg.message = message
        self._send_message(msg)

    def set_status(self, status_id, message):
        debug.info('Setting status to {0}, message: \'{1}\''.format(status_id, message))
        status = im.Status()
        status.code = status_id
        status.message = message
        status.idle = 0
        self._set_status(status)

    def toggle_visibility(self, invisible):
        if invisible:
            debug.info('Switch visibility to invisible')
            self._toggle_visible(True)
        else:
            debug.info('Switch visibility to visible')
            self._toggle_visible(False)