from flask import Flask
from flask_restful import Resource, Api, abort, reqparse
from flask_restful_swagger import swagger
from imapclient import IMAPClient
import imaplib, argparse

# Recovery arguments
parser = argparse.ArgumentParser()
parser.add_argument("host")
parser.add_argument("user")
parser.add_argument("password")
args = parser.parse_args()

# Init API
app = Flask(__name__)
api = swagger.docs(Api(app), apiVersion = '1.0')

# Init variables
rights = 'lrswipkxtecda'
parser = reqparse.RequestParser()
parser.add_argument('newname')
parser.add_argument('quota')

##
# IMAPConfig class
# This class contains the IMAP configuration
##
class ImapConfig:
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password

    def get_conn(self):
        conn = imaplib.IMAP4(self.host)
        conn.login(self.user, self.password)
        return conn

    def logout(self):
        conn = imaplib.IMAP4(self.host)
        conn.logout()
        return conn


class ImapUtil:
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password

    def get_sep(self):
        server = IMAPClient(self.host)
        server.login(self.user, self.password)
        flags, sep, name = server.namespace()
        namespace = str(sep).split(',')[0].strip('(u"')
        return namespace

    def check_mbox(self, mailbox):
        server = IMAPClient(self.host)
        server.login(self.user, self.password)
        return server.folder_exists(mailbox)

# Configuration Initialisation
connFactory = ImapConfig(args.host, args.user, args.password)
utilFactory = ImapUtil(args.host, args.user, args.password)


##
# Mailboxes class
# This class contains global actions for mailboxes
##
class MailboxesList(Resource):
    def get(self):
	'''This method list all mailboxes stored on args.host server'''
        conn = None
        try:
            conn = connFactory.get_conn()
            res, data = conn.list()
            if res == 'NO':
                abort(404, message = "The IMAP server hasn't got mailboxes")
            else:
	            return { "OK" : [e.split(' ')[2] for e in data] }, 200
        finally:
            if conn is not None:
                conn.logout()

##
# Mailbox class
# This class contains all actions of mailboxes management (create/update/delete)
##
class Mailbox(Resource, ImapUtil):
    def get(self, username):
        conn = None
        try:
            conn = connFactory.get_conn()
            namespace = utilFactory.get_sep().strip("'")
            user = namespace + username
            exists = utilFactory.check_mbox(user)
            if not exists:
                abort(406, message="Maibox {} doesn't exist".format(username))
            else:
                return { "OK" : "Mailbox " + username + " exists" }, 200
        finally:
            if conn is not None:
                conn.logout()

    def post(self, username):
        conn = None
        try:
            conn = connFactory.get_conn()
            namespace = utilFactory.get_sep().strip("'")
            user = namespace + username
            res, data = conn.create(user)
            if res == 'NO':
                abort(400, message = data)
            else:
                return { "OK" : "Mailbox has been created" }, 201
        finally:
            if conn is not None:
                conn.logout()

    def delete(self, username):
        conn = None
        try:
            conn = connFactory.get_conn()
            namespace = utilFactory.get_sep().strip("'")
            user = namespace + username
            conn.setacl(user, args.user, rights)
            res, data = conn.delete(user)
            if res == 'NO':
                abort(500, message = data)
            else:
                return { "OK" : "Mailbox has been deleted" }, 201
        finally:
            if conn is not None:
                conn.logout()

    def put(self, username):
        conn = None
        try:
            args = parser.parse_args()
            conn = connFactory.get_conn()
            namespace = utilFactory.get_sep().strip("'")
            olduser = namespace + username
            newuser = namespace + args['newname']
            if olduser == newuser:
                return { "OK" : "{} and {} are identical".format(olduser, newuser)}, 304
            res, data = conn.rename(olduser, newuser)
            if res == 'NO':
                abort(406, message = "Mailbox {} does not exist".format(username))
            else:
                return { "OK" : "Mailbox " + olduser + " has been renamed to " + newuser }, 200

        finally:
            if conn is not None:
                conn.logout()

##
# Quota class
# This class contains all actions for quota management
##
class Quota(Resource):
    def get(self, username):
        conn = None
        try:
            conn = connFactory.get_conn()
            namespace = utilFactory.get_sep().strip("'")
            user = namespace + username
            res, data = conn.getquota(user)
            if res == 'NO':
                abort(404, message = data )
            else:
                return { "OK" : data }, 200
        finally:
            if conn is not None:
                conn.logout()

    def put(self, username):
        conn = None
        try:
            args = parser.parse_args()
            conn = connFactory.get_conn()
            namespace = utilFactory.get_sep().strip("'")
            user = namespace + username
            quota = args['quota']
            res, data = conn.setquota(user, '(STORAGE % s)' % quota)
            if res == 'NO':
                abort(404, message = data)
            else:
                return { "OK" : str(username + "'s mailbox quota has been updated. The new value is " + quota +" octets")}, 200
        finally:
            if conn is not None:
                conn.logout()


##
# Endpoints API adding
##
api.add_resource(MailboxesList, '/mailboxes')
api.add_resource(Mailbox, '/mailbox/<username>', methods=['GET', 'POST', 'DELETE', 'PUT'])
api.add_resource(Quota, '/quota/<username>', methods=['GET', 'PUT'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
