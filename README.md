# imap-api

This tool is an IMAP api based on [Flask-Restful](http://flask-restful-cn.readthedocs.org/en/0.3.4/).

I use imaplib and IMAPClient python module to deal with an IMAP server.

With this tool, you can run some IMAP commands to manage your IMAP server. Indeed, you can :
* List all mailboxes on the IMAP server
* Manage mailboxes/mailshares
  * Create
  * Delete
  * Rename
* Manage quotas
  * Get current quota (maibox, or root mailbox)
  * Set a new quota

If you want to test it, have a look [here](https://imap-api.drix.fr/docs/).

This documentation is baed on [Swagger UI](http://swagger.io/getting-started/).
I think it's a very great tool to create API documentation, that's why I chose it to create IMAP-API documentation.

Have Fun :)

_PS : This API was tested with a cyrus-imapd server. The test with dovecot is coming..._
