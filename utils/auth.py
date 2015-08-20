import hashlib
from string import letters
from random import choice

SECRET_KEY = 'schaferlab'
HASHER = lambda s: hashlib.sha256(s).hexdigest()
SEP = '|'


def make_salt():
    return ''.join(choice(letters) for _ in range(5))


def make_secure_val(s, salt=None):
    if salt is None:
        salt = make_salt()

    return SEP.join([s, salt, HASHER(s + salt)])


def check_secure_val(s):
    original, salt, hashcode = s.split(SEP)

    if s == make_secure_val(original, salt):
        return original


def make_pw_hash(name, pword, salt=None):
    if salt is None:
        salt = make_salt()

    hashcode = HASHER(name + pword + salt)
    return SEP.join([salt, hashcode])


def is_valid_pw_hash(name, pword, hashcode):
    salt, original = hashcode.split(SEP)
    return make_pw_hash(name, pword, salt) == hashcode
