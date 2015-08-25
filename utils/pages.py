from baseclasses import Handler
from models import *
from collections import defaultdict
from itertools import chain
from google.appengine.api import memcache
from connectome import generate_and_cache_edgelist


class WelcomePage(Handler):
    def get(self):
        self.render('welcome.html', admin=True)


class SrcExpressionPage(Handler):
    def get(self):

        ma_to_src_genes = SourceGene.get_all_by_monoamine()  #
        # self.write('ma_to_src_genes = ' + str(ma_to_src_genes))
        src_expr = GeneExpression.get_genes([d['gene'] for d in chain(*ma_to_src_genes.values())])
        # self.write('src_expr = ' + str(src_expr))

        self.render('src_expression.html', admin=True, ma_to_src_genes=ma_to_src_genes, src_expr=src_expr)


class TgtExpressionPage(Handler):
    def get(self):

        ma_to_rec_genes = Receptor.get_all_by_monoamine()  #
        # self.write('ma_to_src_genes = ' + str(ma_to_src_genes))
        rec_expr = GeneExpression.get_genes([d['gene'] for d in chain(*ma_to_rec_genes.values())])
        # self.write('src_expr = ' + str(src_expr))

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
        edgelist = memcache.get('edgelist')
        if not edgelist:
            self.write('Generating data...')
            edgelist = generate_and_cache_edgelist()
            self.redirect('/data')

        if not edgelist:
            self.write('Sorry, edgelist could not be generated!')
        else:
            self.display_csv(edgelist)

    def display_csv(self, csv):
        self.write(csv.replace('\r\n', '<br>'))





