from models import SourceGene, Receptor, GeneExpression
import os
from google.appengine.ext import db
import warnings
import json
import csv
import logging

DATA_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'initial_setup')
# DATA_ROOT = os.path.join('/', 'initial_setup')
MONOAMINE_FILE_ROOT = 'monoamine_network_{}.csv'
CLASS_TO_NEURON_FILENAME = 'class_to_neurons.json'


def purge_tables():
    tables = [SourceGene, Receptor, GeneExpression]

    for table in tables:
        q = table.all()
        q.get()
        for row in q:
            row.delete()


def gen_data_rows(file_obj):
    rd = csv.reader(file_obj)
    for row in rd:
        if row[0] != '':
            yield row


def sanitise(*args):
    return [str(arg).decode('utf-8').strip() for arg in args]


def populate_SourceGene_Receptor():
    sheet_names = ['5-HT', 'DA', 'OA', 'TA']

    for sheet_name in sheet_names:
        with open(os.path.join(DATA_ROOT, MONOAMINE_FILE_ROOT.format(sheet_name))) as f:
            for row in gen_data_rows(f):
                monoamine, gene_type, name, wbid, citation = sanitise(
                    row[0], row[1], row[2], row[3], row[7] if len(row) > 7 else '')

                if not citation:
                    citation = 'Unpublished'

                if gene_type == 'source':
                    entry = SourceGene(gene=name, wbid=wbid, monoamine=monoamine, citation=citation, added_by='Admin')
                elif gene_type == 'receptor':
                    entry = Receptor(gene=name, wbid=wbid, monoamine=monoamine, citation=citation, added_by='Admin')
                else:
                    warnings.warn('Unknown gene_type {}'.format(gene_type))
                    continue

                entry.put()


def populate_GeneExpression():
    # logging.error('Getting neurone class mappings')
    with open(os.path.join(DATA_ROOT, CLASS_TO_NEURON_FILENAME)) as f:
        class_to_neurons = json.load(f)

    sheet_names = ['Receptor Expr', 'Monoamine Expr']

    for sheet_name in sheet_names:
        # logging.error('Opening sheet {}'.format(sheet_name))
        with open(os.path.join(DATA_ROOT, MONOAMINE_FILE_ROOT.format(sheet_name))) as f:
            for row in gen_data_rows(f):

                # logging.error('Processing row: \n\t {}'.format(str(row)))

                gene, neuron_class, wbid, citation = sanitise(
                    row[1], row[2], row[3], row[4] if len(row) > 4 else ''
                )

                if not citation:
                    citation = 'Unpublished'

                for neuron_name in class_to_neurons.get(neuron_class, [neuron_class]):
                    entry = GeneExpression(gene=gene, neuron=neuron_name, citation=citation, wbid=wbid, added_by='Admin')

                    entry.put()


def populate_tables():
    populate_GeneExpression()
    populate_SourceGene_Receptor()


def main(purge=False):
    if purge:
        # logging.error('Purging tables')
        purge_tables()

    # logging.error('Populating tables')
    populate_tables()