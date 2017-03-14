from bureaucrate import init

mailboxes_base = '~/mail/test_account'
mailboxes_names = ['INBOX', 'notifications', 'love of my life']

mailboxes = init(mailboxes_base, mailboxes_names)

for message in mailboxes['INBOX']:
    # move the message to mailbox _notifications_, and mark as read if the word 'notification' is in the subject
    message.subject_has('notification').mark_as_read().move_to('notifications')

    # sort every mail from so@gmail.com to 'love of my life' as starred
    message.is_from('so@gmail.com').move_to('love of my life')

# delete mails older than 60 days in mb 'notifications'
for message in mailboxes['notifications']:
    message.older_than('60d').delete()

for message in mailboxes['Spam']:
    message.older_than('60d').delete()
