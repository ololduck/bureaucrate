from symbol import decorator

from bureaucrate import init

mailboxes_base = '~/mail2/paulollivier.fr'
mailboxes_names = ['INBOX', 'Trash']

mailboxes = init(mailboxes_base, mailboxes_names)

for message in mailboxes['Trash']:
    message.delete()
