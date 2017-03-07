from symbol import decorator

from bureaucrate import init

mailboxes_base = '~/mail2/main'
mailboxes_names = ['INBOX', 'Trash']

mailboxes = init(mailboxes_base, mailboxes_names)

for message in mailboxes['INBOX']:
    # move the message to mailbox _notifications_, and mark as read if the word 'notification' is in the subject
    message.subject_has('notification').mark_as_read().move_to(mailboxes['Trash'])

    # sort every mail from so@gmail.com to 'love of my life' as starred
#    message.is_from('so@gmail.com').move_to(mailboxes['love of my life'])

for message in mailboxes['Trash']:
    message.older_than('60d').delete()
