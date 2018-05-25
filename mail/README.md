# Mail module

This API provides functionality to save and send mails.

This module allows:

- add mails to database
- send mails from database

View API details in the file [Robin8_BlockChain_MAIL_API.md](Robin8_BlockChain_MAIL_API.md).

## Installation

Create virtualenv and install needed libraries from the requirements.txt:

```bash
cd mail
virtualenv --python=python3.6 venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Quick start

run index.py:

```
python index.py  --- run server
python email_new.py start  --- strat daemon
python email_new.py stop  --- stop daemon
python email_new.py restart  --- restrat daemon
```