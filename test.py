import os
import secrets

clave = secrets.token_hex(64)

api_key = secrets.token_urlsafe(64)

print("Clave HEX 64bits:", clave)

print("Clave URLSAFE 64bits:", api_key)