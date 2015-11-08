from flask import Flask
from flask_restful import Resource, Api
import imaplib, argparse, re

# Recovery arguments
parser = argparse.ArgumentParser()
parser.add_argument("host")
parser.add_argument("user")
parser.add_argument("password")
args = parser.parse_args()

# Init API
app = Flask(__name__)
api = Api(app)

# Connection establishment
conn = None
conn = imaplib.IMAP4(args.host)
print "OK\nThe connexion with " + args.host + " is established"
conn.login(args.user, args.password)
print "OK\n"+ args.user +" is authenticated"

# Init variables
rights = 'lrswipkxtecda'

##
# Mailboxes class
# This class contains global actions for mailboxes
##
class MailboxesList(Resource):
    def get(self):
        res = conn.list() 
	return [e.split(' ')[2] for e in res[1]]
##
# Mailbox class
# This class contains all actions of mailboxes management (create/update/delete)
##
class Mailbox(Resource):
    def get(self, username):
	error = None
	user = "user/" + username
	res = conn.list(user)
	if str(res[1]) in '[None]':
	   return "Maibox " + username + " doesn't exist"
	else:
	   return "Mailbox " + username + " exists"

    def post(self, username):
	error = None
	user = "user/" + username
	res = conn.create(user)
	if res[0] == 'NO':
	   error = str(res[1])
	   return error
	else:
	   return "Mailbox has been created"

    def delete(self, username):
	error = None
	user = "user/" + username
	conn.setacl(user, args.user, rights)
	res = conn.delete(user)
	if res[0] == 'NO':
	   error = str(res[1])
	   return error
	else:
           return "Mailbox has been deleted"

    def put(self, oldname, newname):
	error = None
	olduser = 'user/' + oldname
	newuser = 'user/' + newname
	res = conn.rename(olduser, newuser)
	if res[0] == 'NO':
	    error = str(res[1])
	    return error
	else:
	    return "Mailbox " + oldname + " has been renamed to " + newname

##
# Quota class
# This class contains all actions for quota management
##
class Quota(Resource):
    def get(self, username):
    	error = None
	user = 'user/' + username
    	res = conn.getquota(user)
    	if res[0] == 'NO':
    	    error = str(res[1])
    	    return error
    	else:
    	    return str(res[1])

    def put(self, username, quota):
        error = None
	user = 'user/' + username
        res = conn.setquota(user, '(STORAGE % s)' % quota)
        if res[0] == 'NO':
            error = str(res[1])
            return error
        else:
            r = str(username + "'s mailbox quota has been updated. The new value is " + quota +" octets")
	    return r

##
# Command class
# This class contains quit and connect command 
##
class Command(Resource):
    def get(self):
        error = None
        res = conn.logout()
        if res[0] == 'NO':
            return error
        else:
            return "The connexion with " + args.host + " is closed now"

    def post(self):
	error = None
	conn = imaplib.IMAP4(args.host)
	user = 'cyrus'
	passwd = 'cyrus'
	conn.login(user, passwd)
	return "The connexion with " + args.host + " is established"


##
# Endpoints API adding
##
api.add_resource(MailboxesList, '/mailboxes/')
api.add_resource(Mailbox, '/mailbox/<username>/')
api.add_resource(Mailbox, '/mailbox/create/<username>/', methods=['POST'], endpoint='create')
api.add_resource(Mailbox, '/mailbox/delete/<username>/', methods=['DELETE'], endpoint='delete')
api.add_resource(Mailbox, '/mailbox/rename/<oldname>/<newname>/', methods=['PUT'], endpoint='rename')
api.add_resource(Quota, '/quota/<username>/')
api.add_resource(Quota, '/quota/<username>/<quota>/', methods=['PUT'], endpoint='setquota')
api.add_resource(Command, '/quit/')
api.add_resource(Command, '/connect/', methods=['POST'], endpoint='connect')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
