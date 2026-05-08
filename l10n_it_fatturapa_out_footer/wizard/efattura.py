from odoo.addons.l10n_it_account.tools.account_tools import encode_for_export
from odoo.addons.l10n_it_fatturapa_out.wizard.efattura import EFatturaOut


class EFatturaOutFooter(EFatturaOut):
    def get_template_values(self):
        template_values = super().get_template_values()
        get_causale_ori = template_values.get("get_causale")

        def get_causale(invoice):
            res = []
            if get_causale_ori:
                res = get_causale_ori(invoice)
            if invoice.company_id.report_footer:
                from lxml import html

                try:
                    footer_text = "\n".join(
                        text.strip()
                        for text in html.fromstring(
                            invoice.company_id.report_footer
                        ).xpath("//text()")
                    )
                except Exception:
                    footer_text = ""
                # >8 end meanwhile

                # max length of Causale is 200
                caus_list = footer_text.split("\n")
                for causale in caus_list:
                    if not causale:
                        continue
                    causale_list_200 = [
                        causale[i : i + 200] for i in range(0, len(causale), 200)
                    ]
                    for causale200 in causale_list_200:
                        # Remove non latin chars, but go back to unicode string,
                        # as expected by String200LatinType
                        causale = encode_for_export(causale200, 200)
                        res.append(causale)

            return res

        template_values.update({"get_causale": get_causale})
        return template_values
