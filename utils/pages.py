from baseclasses import Handler
from models import *
from collections import defaultdict


class WelcomePage(Handler):
    def get(self):
        self.render('welcome.html', admin=True)


class SrcExpressionPage(Handler):
    def get(self):
        self.render('src_expression.html', admin=True, ma_to_src_genes=ma_to_src_genes, src_expr=src_expr)


class TgtExpressionPage(Handler):
    def get(self):
        self.render('tgt_expression.html', admin=True)


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
        self.render('data.html', admin=True)