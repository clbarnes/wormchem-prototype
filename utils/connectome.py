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


def generate_and_cache_edgelist():
    output = io.BytesIO()
    writer = csv.writer(output)
    writer.writerow(['source_node', 'target_node', 'monoamine', 'receptor'])
    for edge in generate_edges():
        writer.writerow(edge)

    edgelist = output.getvalue().strip('\r\n')

    memcache.set('edgelist', edgelist)

    return edgelist