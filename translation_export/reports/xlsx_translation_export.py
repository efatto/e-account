from odoo import _, fields, models


class XlsxTranslationExport(models.AbstractModel):
    _name = "report.translation_export.xlsx_translation_export"
    _inherit = "report.report_xlsx.abstract"
    _description = "Report Product Translation XLSX"

    def generate_xlsx_report(self, workbook, data, lines):
        langs = self.env["res.lang"].with_context(active_test=True).search([])
        products = self.env["product.product"].search([])
        sheet = workbook.add_worksheet(_("Translations"))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_column(0, 0, 20)
        for i, _lang in enumerate(langs):
            sheet.set_column(i, i, 20)
        border_style = workbook.add_format({"border": 1})
        title_style = workbook.add_format(
            {"bold": False, "bg_color": "#C0C0C0", "border": 1}
        )

        # header
        sheet_title = [
            _("Code"),
        ]
        for lang in langs:
            sheet_title.append(
                lang.name,
            )
        i = 0
        sheet.merge_range(
            i,
            0,
            i,
            len(langs),
            _("Translation %s") % (fields.Date.today().strftime("%d/%m/%Y"),),
            title_style,
        )
        i += 1
        sheet.write_row(i, 0, sheet_title, title_style)
        sheet.freeze_panes(2, 0)
        i += 1
        for product in products:
            sheet.write(i, 0, product.default_code or "", border_style)
            for il, lang in enumerate(langs):
                sheet.write(
                    i,
                    1 + il,
                    product.with_context(lang=lang.code).name or "",
                    border_style,
                )
            i += 1
