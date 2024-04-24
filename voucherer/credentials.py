#! /usr/bin/env python3

from dataclasses import dataclass
import rstr

# To avoid visual confusion, this uses only lower-case alphabetical characters,
# and excludes i, l, 1, o, and 0.
DEFAULT_USERNAME_TEMPLATE = r'[abcdefghjkmnpqrstuvwxyz23456789]{4}'
DEFAULT_PASSWORD_TEMPLATE = DEFAULT_USERNAME_TEMPLATE

@dataclass
class Credentials:
    username: str
    password: str

def generate(usernameTemplate: str, passwordTemplate: str) -> Credentials:
    return Credentials(rstr.xeger(usernameTemplate), rstr.xeger(passwordTemplate))
