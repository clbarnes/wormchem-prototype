from baseclasses import Handler, jinja_env
from models import *
from collections import defaultdict
from itertools import chain
from google.appengine.api import memcache
from connectome import generate_and_cache_edgelist
import cgi


def wbid_to_link(wbid):
    escaped_wbid = cgi.escape(wbid)
    if wbid in ['', '?']:
        return 'no WBID'
    elif 'expr' in wbid.lower():
        wb_type = 'species/all/expr_pattern'
    elif 'wbgene' in wbid.lower():
        wb_type = 'species/all/gene'
    elif 'wbpaper' in wbid.lower():
        wb_type = 'resources/paper'
    else:
        return '<a href="{}">{}<a>'.format('http://www.wormbase.org/search/all/' + escaped_wbid, escaped_wbid)

    url = 'http://www.wormbase.org/{}/{}'.format(wb_type, escaped_wbid)
    return '<a href="{}">{}<a>'.format(url, escaped_wbid)


jinja_env.globals['wbid_to_link'] = wbid_to_link


class WelcomePage(Handler):
    def get(self):
        self.render('welcome.html', admin=True)


class SrcExpressionPage(Handler):
    def get(self):
        ma_to_src_genes = SourceGene.get_all_by_monoamine()  #
        src_expr = GeneExpression.get_genes([d['gene'] for d in chain(*ma_to_src_genes.values())])

        self.render('src_expression.html', admin=True, ma_to_src_genes=ma_to_src_genes, src_expr=src_expr)


class TgtExpressionPage(Handler):
    def get(self):
        ma_to_rec_genes = Receptor.get_all_by_monoamine()  #
        rec_expr = GeneExpression.get_genes([d['gene'] for d in chain(*ma_to_rec_genes.values())])

        self.render('tgt_expression.html', admin=True, ma_to_rec_genes=ma_to_rec_genes, rec_expr=rec_expr)


class MaToReceptorPage(Handler):
    def get(self):
        results = db.GqlQuery('SELECT * FROM Receptor ORDER BY gene')
        ma_to_receptors = defaultdict(list)
        for result in results:
            ma_to_receptors[result.monoamine].append(result)
        self.render('ma_to_receptor.html', admin=True, ma_to_receptors=dict(ma_to_receptors), logged_in=True, receptor='')

    def post(self):
        self.render('ma_to_receptor.html', admin=True, logged_in=True, error='Sorry, not implemented yet')


class SignupPage(Handler):
    def get(self):
        self.render('signup.html', admin=True)

    def post(self):
        self.render('signup.html', admin=True, error='Sorry, not implemented yet')


class LoginPage(Handler):
    def get(self):
        self.render('login.html', admin=True)

    def post(self):
        self.render('login.html', admin=True, error='Sorry, not implemented yet')


class AdminPage(Handler):
    def get(self):
        self.render('admin.html', admin=True)


class DataPage(Handler):
    def get(self):
        edgelist = memcache.get('edgelist_formatted')
        if not edgelist:
            self.write('Generating data...')
            edgelist = generate_and_cache_edgelist(formatted=True)
            self.redirect('/data')

        if not edgelist:
            self.write('Sorry, edgelist could not be generated!')
        else:
            self.write(edgelist)