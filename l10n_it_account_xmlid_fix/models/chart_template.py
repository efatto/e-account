import csv
import logging
from pathlib import Path

from odoo import models, modules

_logger = logging.getLogger(__name__)


class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    def _load(self, template_code, company, install_demo, force_create=True):
        self._pre_install_l10n_it_fix_xmlids()
        return super()._load(template_code, company, install_demo, force_create)

    def _pre_install_l10n_it_fix_xmlids(self):  # noqa: C901
        """
        Search for existing records (account, tax, group, fiscal position)
        and assign them the xmlid defined in l10n_it to avoid duplicates.
        """
        l10n_it_path = modules.get_module_path("l10n_it")
        if not l10n_it_path:
            _logger.warning("Module l10n_it not found.")
            return

        # Configuration of files to process
        csv_configs = [
            {
                "file": "account.account-it.csv",
                "model": "account.account",
                "search_field": "code",
                "csv_field": "code",
            },
            {
                "file": "account.tax-it.csv",
                "model": "account.tax",
                "search_field": "name",
                "csv_field": "name",
            },
            {
                "file": "account.tax.group-it.csv",
                "model": "account.tax.group",
                "search_field": "name",
                "csv_field": "name",
            },
            {
                "file": "account.fiscal.position-it.csv",
                "model": "account.fiscal.position",
                "search_field": "name",
                "csv_field": "name",
            },
        ]

        for config in csv_configs:
            for company in self.env["res.company"].search([]):
                csv_path = Path(l10n_it_path) / "data" / "template" / config["file"]
                if not csv_path.exists():
                    _logger.warning("CSV file not found: %s", str(csv_path))
                    continue

                _logger.info("Processing %s for XMLID fix", config["file"])
                with csv_path.open(encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        xml_id = f"{company.id}_{row.get('id')}"
                        search_value = row.get(config["csv_field"])

                        if not xml_id or not search_value:
                            _logger.info(
                                f"Record not found for xml_id {xml_id} in company "
                                f"{company.name}"
                            )
                            continue

                        # Search for the record by the specified field
                        if config["model"] == "account.account":
                            search_value = search_value + "00"
                        record = self.env[config["model"]].search(
                            [(config["search_field"], "=", search_value)], limit=1
                        )

                        if not record:
                            _logger.info(
                                f"No record found for search value {search_value} in "
                                f"{config['model']} in company {company.name}"
                            )
                            continue

                        full_xml_id = f"account.{xml_id}"
                        existing_xmlid = self.env.ref(
                            full_xml_id, raise_if_not_found=False
                        )

                        if not existing_xmlid:
                            _logger.info(
                                "Assigning XMLID %s to %s (%s: %s)",
                                full_xml_id,
                                config["model"],
                                config["search_field"],
                                search_value,
                            )
                            self.env["ir.model.data"].create(
                                {
                                    "name": xml_id,
                                    "module": "account",
                                    "model": config["model"],
                                    "res_id": record.id,
                                    "noupdate": True,
                                }
                            )
                        elif existing_xmlid != record:
                            _logger.warning(
                                "XMLID %s already exists for %s but points to "
                                "another record (%s instead of %s)",
                                full_xml_id,
                                config["model"],
                                existing_xmlid.id,
                                record.id,
                            )

        # Handling of Odoo standard journals created by account.chart.template
        # In Odoo 18 standard journals are sale, purchase, general, exch,
        # caba, bank, cash, stj. During the installation of l10n_it,
        # if they already exist, the installer tries to recognize them via XMLID.
        # In Odoo 18 the expected XMLID is account.COMPANYID_XMLID.
        journals_to_fix = [
            {"xml_id": "sale", "type": "sale", "codes": ["FATT", "INV"]},
            {"xml_id": "purchase", "type": "purchase", "codes": ["ACQ", "BILL"]},
            {"xml_id": "general", "type": "general", "codes": ["VARIE", "MISC"]},
            {"xml_id": "exch", "type": "general", "codes": ["CAMBI", "EXCH"]},
            {"xml_id": "caba", "type": "general", "codes": ["CABA"]},
            {"xml_id": "bank", "type": "bank", "codes": ["BNK4", "BANK"]},
            {"xml_id": "cash", "type": "cash", "codes": ["CSH1", "CASH"]},
            {"xml_id": "inventory_valuation", "type": "general", "codes": ["STJ"]},
        ]

        for company in self.env["res.company"].search([]):
            for j_conf in journals_to_fix:
                # Search for an existing journal by code or type
                journal = self.env["account.journal"].search(
                    [
                        ("code", "in", j_conf["codes"]),
                        ("company_id", "=", company.id),
                    ],
                    limit=1,
                )

                if not journal:
                    journal = self.env["account.journal"].search(
                        [
                            ("type", "=", j_conf["type"]),
                            ("company_id", "=", company.id),
                        ],
                        limit=1,
                    )

                if not journal:
                    _logger.info(
                        f"Journal not found for {j_conf['type']} in company "
                        f"{company.name}"
                    )
                    continue

                if journal:
                    xml_id_name = f"{company.id}_{j_conf['xml_id']}"
                    full_xml_id = f"account.{xml_id_name}"
                    existing_xmlid = self.env.ref(full_xml_id, raise_if_not_found=False)

                    if not existing_xmlid:
                        _logger.info(
                            "Assigning XMLID %s to journal %s (type: %s)",
                            full_xml_id,
                            journal.name,
                            j_conf["type"],
                        )
                        self.env["ir.model.data"].create(
                            {
                                "name": xml_id_name,
                                "module": "account",
                                "model": "account.journal",
                                "res_id": journal.id,
                                "noupdate": True,
                            }
                        )
