
from cStringIO import StringIO
from openerp import http
from openerp.addons.web.controllers.main import \
    serialize_exception, content_disposition
from openerp.http import request


class DownloadXlsReport(http.Controller):

    @http.route('/l10n_it_account_invoice_statement/export_report/'
                'download_xls_report', type='http', auth="user")
    @serialize_exception
    def download_report(self, **kw):
        filename = 'first_sheet'
        fp = StringIO()
        workbook = request.session.get('wb')
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        if not data:
            return request.not_found()
        else:
            return request.make_response(
                data,
                [('Content-Type', 'application/octet-stream'),
                ('Content-Disposition', content_disposition(
                    filename + '.xls'))])
