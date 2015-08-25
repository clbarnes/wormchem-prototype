from google.appengine.ext import db
from google.appengine.api import memcache
from auth import *
from datetime import datetime
import logging
from collections import defaultdict


source_gene_key = db.Key.from_path('wormchem', 'sourcegene')
receptor_key = db.Key.from_path('wormchem', 'receptor')
ma_to_receptor_key = db.Key.from_path('wormchem', 'matoreceptor')
gene_expression_key = db.Key.from_path('wormchem', 'geneexpression')


def users_key(group='default'):
    return db.Key.from_path('users', group)


class DeletableEntry(db.Model):
    deleted_on = db.DateTimeProperty()
    deleted_by = db.StringProperty()

    def delete(self, deleter):
        self.deleted_on = datetime.now()
        self.deleted_by = deleter


class ReviewableEntry(db.Model):
    added_on = db.DateTimeProperty(auto_now_add=True)
    added_by = db.StringProperty(required=True)
    reviewed_by = db.StringProperty()
    reviewed_on = db.DateTimeProperty()

    def review(self, reviewer):
        self.reviewed_by = reviewer
        self.reviewed_on = datetime.now()


class GeneEntry(db.Model):
    gene = db.StringProperty(required=True)
    citation = db.StringProperty(required=True)
    wbid = db.StringProperty()


class UniqueGeneEntry(GeneEntry, db.Model):
    # __metaclass__ = abc.ABCMeta

    @classmethod
    def by_name(cls, gene_name):
        cls.all().filter('gene = ', gene_name).get()  # todo: not sure about this

    @classmethod
    def get_all_by_monoamine(cls):
        """
        Return a dictionary whose keys are monoamines and values are lists.

        The items of these lists are dictionaries whose keys are 'gene', 'citation' and 'wbid' and values are the corresponding strings for a single source gene.

        :return: d
        :rtype: dict of lists of dicts
        """
        d = defaultdict(list)
        query = cls.all().order('deleted_on').order('gene')  # todo ignore deleted entries
        for row in query:
            d[row.monoamine.title()].append({'gene': row.gene, 'citation': row.citation, 'wbid': row.wbid})

        return dict(d)


class SourceGene(UniqueGeneEntry, DeletableEntry, ReviewableEntry, db.Model):
    monoamine = db.StringProperty(required=True)


class Receptor(UniqueGeneEntry, DeletableEntry, ReviewableEntry, db.Model):
    monoamine = db.StringProperty(required=True)


class GeneExpression(GeneEntry, DeletableEntry, ReviewableEntry, db.Model):
    neuron = db.StringProperty(required=True)

    @classmethod
    def get_genes(cls, gene_list):
        """
        Return a dictionary whose keys are the genes in gene_list and whose values are lists of dictionaries.

        Each item in the list is a dictionary representing a cell in which the gene is expressed, with keys 'node', 'wbid' and 'citation'.

        :param gene_list: A list of gene names
        :type gene_list: list of str
        :return: d
        :rtype: dict of lists of dicts
        """
        logging.error('gene_list = ' + str(gene_list))
        d = defaultdict(list)

        # gene_list = sorted(gene_list, reverse=True)
        # in_filter_list = []
        # while len(gene_list) > 30:
        #     in_filter_list.append(gene_list[:30])
        #     gene_list = gene_list[30:]
        # in_filter_list.append(gene_list)
        #
        # queries = [cls.all().filter('gene IN ', in_filter).order('gene') for in_filter in in_filter_list]
        #
        # for query in queries:

        query = cls.all().filter('gene IN ', list(set(gene_list))).order('gene')  # todo ignore deleted entries
        for row in query:
            d[row.gene].append({'node': row.neuron, 'wbid': row.wbid, 'citation': row.citation})

        logging.error('expression dict = ' + str(d))

        return dict(d)

    @classmethod
    def get_all_by_gene(cls):
        """

        :return: A dictionary whose keys are genes and values are lists of neurons where the gene is expressed
        """
        d = defaultdict(list)
        query = cls.all()  # todo ignore deleted entries
        for row in query:
            d[row.gene].append(row.neuron)

        return dict(d)


class User(DeletableEntry, db.Model):
    username = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty(required=True)
    institution = db.StringProperty()
    made_admin_on = db.DateTimeProperty()
    made_admin_by = db.StringProperty()

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