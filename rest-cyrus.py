#!/usr/bin/python

from flask import Flask
from flask_restful import Resource, Api, abort, reqparse
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
api = Api(app)

# Init variables
rights = 'lrswipkxtecda'
parser = reqparse.RequestParser()

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

    def post(self):
        conn = None
        name = "mailbox"
        try:
            parser.add_argument('username', location='form')
            parser.add_argument('mailshare', location='args')
            args = parser.parse_args()
            conn = connFactory.get_conn()
            namespace = utilFactory.get_sep().strip("'")

            tmp = args['mailshare']
            mailshare = int(tmp)

            if 0 < mailshare > 1:
                abort(406, message = "The mailshare argument must be equal 0 or 1")
            user = namespace + args['username']

            if mailshare == 1:
                user = args['username']
                name = "mailshare"

            res, data = conn.create(user)
            if res == 'NO':
                abort(400, message = data)
            else:
                return { "OK" : "The {} {} has been created".format(name, args['username']) }, 201
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
        name = "mailbox"
        try:
            parser.add_argument('mailshare', location='args')
            args = parser.parse_args()
            conn = connFactory.get_conn()
            namespace = utilFactory.get_sep().strip("'")

            tmp = args['mailshare']
            mailshare = int(tmp)
            if 0 < mailshare > 1:
                abort(406, message = "The mailshare argument must be equal 0 or 1")

            user = namespace + username

            if mailshare == 1:
                user = username
                name = "mailshare"

            exists = utilFactory.check_mbox(user)
            if not exists:
                abort(406, message="The {} {} doesn't exist".format(name, username))
            else:
                return { "OK" : "The {} {} exists".format(name, username) }, 200
        finally:
            if conn is not None:
                conn.logout()

    def delete(self, username):
        conn = None
        name = "mailbox"
        try:
            parser.add_argument('mailshare', location='args')
            arg = parser.parse_args()
            conn = connFactory.get_conn()
            namespace = utilFactory.get_sep().strip("'")

            tmp = arg['mailshare']
            mailshare = int(tmp)
            if 0 < mailshare > 1:
                abort(406, message = "The mailshare argument must be equal 0 or 1")

            user = namespace + username

            if mailshare == 1:
                user = username
                name = "mailshare"

            conn.setacl(user, args.user, rights)
            res, data = conn.delete(user)
            if res == 'NO':
                abort(400, message = data)
            else:
                return { "OK" : "The {} {} has been deleted".format(name, username) }, 201
        finally:
            if conn is not None:
                conn.logout()

    def put(self, username):
        conn = None
        name = "mailbox"
        try:
            parser.add_argument('mailshare', location='args')
            parser.add_argument('newname', location='form')
            args = parser.parse_args()
            conn = connFactory.get_conn()
            namespace = utilFactory.get_sep().strip("'")

            tmp = args['mailshare']
            mailshare = int(tmp)
            if 0 < mailshare > 1:
                abort(406, message = "The mailshare argument must be equal 0 or 1")

            tmp_name = args['newname']
            olduser = namespace + username
            newuser = namespace + tmp_name

            if mailshare == 1:
                olduser = username
                newuser = args['newname']
                name = "mailshare"

            if olduser == newuser:
                return { "OK" : "{} and {} are identical".format(username, args['newname'])}, 304
            res, data = conn.rename(olduser, newuser)
            if res == 'NO':
                abort(406, message = "The {} {} does not exist".format(name, username))
            else:
                return { "OK" : "The {} {} has been renamed to {}".format(name, username, args['newname']) }, 200

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
        name = "mailbox"
        try:
            parser.add_argument('mailshare', location='args')
            args = parser.parse_args()
            conn = connFactory.get_conn()
            namespace = utilFactory.get_sep().strip("'")

            tmp = args['mailshare']

            mailshare = int(tmp)

    #    except TypeError as e:
    #        abort(500, message = e)

            if 0 < mailshare > 1:
                abort(406, message = "The mailshare argument must be equal 0 or 1")

            user = namespace + username

            if mailshare == 1:
                user = username
                name = "mailshare"

            res, data = conn.getquota(user)
            if res == 'NO':
                abort(400, message = data )
            else:
                return { "OK" : data }, 200
        finally:
            if conn is not None:
                conn.logout()

    def put(self, username):
        conn = None
        name = "mailbox"
        try:
            parser.add_argument('mailshare', location='args')
            parser.add_argument('quota', location='form')
            args = parser.parse_args()
            conn = connFactory.get_conn()
            namespace = utilFactory.get_sep().strip("'")

            tmp = args['mailshare']
            mailshare = int(tmp)
            if 0 < mailshare > 1:
                abort(400, message = "The mailshare argument must be equal 0 or 1")

            user = namespace + username

            if mailshare == 1:
                user = username
                name = "mailshare"

            quota = args['quota']
            exists = utilFactory.check_mbox(user)
            if not exists:
                abort(406, message="The {} {} doesn't exist".format(name, username))

            res, data = conn.setquota(user, '(STORAGE % s)' % quota)
            if res == 'NO':
                abort(404, message = data)
            else:
                return { "OK" : "{}'s {} quota has been updated. The new value is {} octets".format(username, name, quota)}, 200
        finally:
            if conn is not None:
                conn.logout()

##
# Endpoints API adding
##
api.add_resource(MailboxesList, '/mailboxes')
api.add_resource(Mailbox, '/mailboxes/<username>')
api.add_resource(Quota, '/quota/<username>', methods=['GET', 'PUT'])

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=9080)
    app.run(host='0.0.0.0', port=9080, debug=True)
