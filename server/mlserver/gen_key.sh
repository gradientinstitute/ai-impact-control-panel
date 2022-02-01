#!/usr/bin/env python3
import secrets

key = secrets.token_hex()
with open('server.secret', 'w') as f:
  f.write(key)

