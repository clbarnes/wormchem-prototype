from google.appengine.ext import db
from google.appengine.api import memcache
from auth import *


source_gene_key = db.Key.from_path('wormchem', 'sourcegene')
receptor_key = db.Key.from_path('wormchem', 'receptor')
ma_to_receptor_key = db.Key.from_path('wormchem', 'matoreceptor')
gene_expression_key = db.Key.from_path('wormchem', 'geneexpression')


def users_key(group='default'):
    return db.Key.from_path('users', group)


class SourceGene(db.Model):
    gene = db.StringProperty(required=True)
    wbid = db.StringProperty(required=True)
    monoamine = db.StringProperty(required=True)
    citation = db.StringProperty(required=True)
    added = db.DateTimeProperty(auto_now_add=True)
    added_by = db.StringProperty(required=True)
    reviewed_by = db.StringProperty()
    reviewed_on = db.DateTimeProperty()
    deleted_on = db.DateTimeProperty()


class Receptor(db.Model):
    gene = db.StringProperty(required=True)
    wbid = db.StringProperty(required=True)
    monoamine = db.StringProperty(required=True)
    citation = db.StringProperty(required=True)
    added = db.DateTimeProperty(auto_now_add=True)
    added_by = db.StringProperty(required=True)
    reviewed_by = db.StringProperty()
    reviewed_on = db.DateTimeProperty()
    deleted_on = db.DateTimeProperty()


class MaToReceptorMapping(db.Model):
    monoamine = db.StringProperty(required=True)
    receptor = db.StringProperty(required=True)
    citation = db.StringProperty(required=True)
    added = db.DateTimeProperty(auto_now_add=True)
    added_by = db.StringProperty(required=True)
    reviewed_by = db.StringProperty()
    reviewed_on = db.DateTimeProperty()
    deleted_on = db.DateTimeProperty()


class GeneExpression(db.Model):
    gene = db.StringProperty(required=True)
    neuron = db.StringProperty(required=True)
    citation = db.StringProperty(required=True)
    added = db.DateTimeProperty(auto_now_add=True)
    added_by = db.StringProperty(required=True)
    reviewed_by = db.StringProperty()
    reviewed_on = db.DateTimeProperty()
    deleted_on = db.DateTimeProperty()


class User(db.Model):
    username = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty(required=True)
    institution = db.StringProperty()
    made_admin_on = db.DateTimeProperty()
    made_admin_by = db.StringProperty()
    deleted_on = db.DateTimeProperty()

    @classmethod
    def register(cls, name, pw, email=None):
        pw_hash = make_pw_hash(name, pw)
        return User(
            parent=users_key(),
            username=name,
            pw_hash=pw_hash,
            email=email
        )

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(int(uid), parent=users_key())

    @classmethod
    def by_name(cls, name):
        return User.all().filter('username =', name).get()

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and is_valid_pw_hash(name, pw, u.pw_hash):
            return u


def sanitise(s):
    return 'test string please ignore'

ma_to_src_genes = {
    'Serotonin': ['ser-1', 'ser-4'],
    'Dopamine': ['dop-1', 'dop-2']
}

src_expr = {
    'ser-1': [{'node': 'RIA',
              'citation': 'this is where a citation should go'}],
    'ser-4': [{'node': 'RIB', 'citation': 'still citing'}],
    'dop-1': [{'node': 'AUA', 'citation': "just keen on citin'"}]
}

ma_to_receptors = {
    'Dopamine': [
        {
            'name': 'dop-1',
            'citation': 'a citation!'
        },
        {
            'name': 'dop-2',
            'citation': 'another citation'
        }
    ],
    'Serotonin': [
        {
            'name': 'ser-1',
            'citation': 'you get the picture'
        }
    ]
}