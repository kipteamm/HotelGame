# Setup
## Add a `config.py` file to hotel/

Provide the following, changing the values is of course allowed
```py
import re


DEBUG = True
ALLOWED_CHARACTERS_REGEX = re.compile(r'^[a-zA-Z0-9_.-]+$')
```

## Add a `secrets.py` file to hotel/

Provide the following, changing the values is of course allowed
```py
SECRET_KEY = "secret_key"
```
