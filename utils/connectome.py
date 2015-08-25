from models import SourceGene, Receptor, GeneExpression
from collections import defaultdict
import csv
import io
from itertools import chain
import os
from google.appengine.api import memcache


def generate_edges():
    """
    Parse the database and generate the monoamine edges.

    :return: Generator which iterates through all monoamine edges (separate edges for separate receptors) in the format (src_node, tgt_node, monoamine, tgt_gene)
    :rtype: generator of tuples
    """
    expr = GeneExpression.get_all_by_gene()

    receptors_by_monoamine = Receptor.get_all_by_monoamine()

    for monoamine, src_gene_dicts_list in SourceGene.get_all_by_monoamine().items():
        for src_node in chain(*[expr[src_gene_dict['gene']] for src_gene_dict in src_gene_dicts_list]):
            for tgt_gene in (d['gene'] for d in receptors_by_monoamine[monoamine]):
                for tgt_node in expr[tgt_gene]:
                    yield src_node, tgt_node, monoamine.lower(), tgt_gene


def generate_and_cache_edgelist(formatted=False):
    edgelist = sorted(generate_edges(), key=lambda s: (s[0], s[1], s[2], s[3]))

    headers = ('source_node', 'target_node', 'monoamine', 'receptor')
    edgelist_formatted = '<br>'.join(','.join(edge) for edge in [headers] + edgelist)

    memcache.set('edgelist', edgelist)
    memcache.set('edgelist_formatted', edgelist_formatted)

    return edgelist_formatted if formatted else edgelist