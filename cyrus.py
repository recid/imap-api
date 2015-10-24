from flask import Flask, request
import imaplib, argparse

parser = argparse.ArgumentParser()
parser.add_argument("host")
parser.add_argument("user")
parser.add_argument("password")
args = parser.parse_args()

app = Flask(__name__)
conn = imaplib.IMAP4(args.host)
print "\nThe connexion with " + args.host + " is established"

conn.login(args.user, args.password)
print args.user +" is authenticated"

rights = 'lrswipkxtecda'

## Mailboxes actions
@app.route('/mailboxes/')
def getmailboxes():
    res = conn.list() 
    if res:
        return "OK \nThis server get mailboxes \n"
    else:
        return "There isn't mailbox on this server"

@app.route('/mailboxes/list/')
def mailboxeslist():
    res = conn.list() 
    return str(res[1])+"\n"

# Mailbox actions
@app.route('/mailbox/<username>/')
def getmailbox(username):
    res = conn.list(username)
    return str(res)+"\n"

@app.route('/mailbox/create/<username>/')
def createmailbox(username):
    error = None
    res = conn.create(username)
    if res[0] == 'NO':
        error = str(res[1])+"\n"
        return error
    else:
        return "Mailbox has been created\n"

@app.route('/mailbox/delete/<username>/')
def deletemailbox(username):
    error = None
    conn.setacl(username,args.user,rights)
    res = conn.delete(username)
    if res[0] == 'NO':
        error = str(res[1])+"\n"
        return error
    else:
        return "Mailbox has been deleted\n"

@app.route('/mailbox/rename/<oldname>/<newname>/')
def renamemailbox(oldname, newname):
    error = None
    res = conn.rename(oldname,newname)
    if res[0] == 'NO':
        error = str(res[1])+"\n"
        return error
    else:
        return "Mailbox " + oldname + " has been renamed to " + newname + "\n"


#conn.close()
#conn.logout()

if __name__ == '__main__':
    app.run()
