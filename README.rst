===============================
bureaucrate
===============================


.. image:: https://img.shields.io/pypi/v/bureaucrate.svg
        :target: https://pypi.python.org/pypi/bureaucrate

.. image:: https://img.shields.io/travis/paulollivier/bureaucrate.svg
        :target: https://travis-ci.org/paulollivier/bureaucrate

.. image:: https://readthedocs.org/projects/bureaucrate/badge/?version=latest
        :target: https://bureaucrate.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/paulollivier/bureaucrate/shield.svg
     :target: https://pyup.io/repos/github/paulollivier/bureaucrate/
     :alt: Updates


A maildir-based executer of rules, destined to sort and automate mail.

Here little sample, taken from `sample_config.py`:

.. code-block:: python
   # delete mails older than 60 days in mb 'notifications'
   for message in mailboxes['notifications']:
       message.older_than('60d').delete()

.. note::
   This is still a heavy work in progress, as documentation is sparse at best.

* Free software: MIT license
* Documentation: https://bureaucrate.readthedocs.io.


Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template. And it's quite nice, you should use it too.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

