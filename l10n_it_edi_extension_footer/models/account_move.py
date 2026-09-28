from odoo import models
from odoo.tools import html2plaintext, is_html_empty


class AccountMove(models.Model):
    _inherit = "account.move"

    def _l10n_it_edi_get_values(self, pdf_values=None):
        res = super()._l10n_it_edi_get_values(pdf_values)
        causale_lines = res["causale_lines"] or []

        if not is_html_empty(self.company_id.report_footer):
            try:
                footer_text = html2plaintext(self.company_id.report_footer)
            except Exception:
                footer_text = ""

            # max length of Causale is 200
            for line in footer_text.splitlines():
                if line.strip():
                    causale_lines.extend(
                        line[i : i + 200] for i in range(0, len(line), 200)
                    )

        res["causale_lines"] = causale_lines

        return res
