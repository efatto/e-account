import csv
import logging
import os

from odoo import api, models, modules

_logger = logging.getLogger(__name__)


class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    @api.model
    def _pre_install_l10n_it_fix_xmlids(self):
        """
        Cerca i record esistenti (account, tax, group, fiscal position)
        e assegna loro l'xmlid definito in l10n_it per evitare duplicati.
        """
        l10n_it_path = modules.get_module_path("l10n_it")
        if not l10n_it_path:
            _logger.warning("Modulo l10n_it non trovato.")
            return

        # Configurazione dei file da processare
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
            csv_path = os.path.join(l10n_it_path, "data", "template", config["file"])
            if not os.path.exists(csv_path):
                _logger.warning("File CSV non trovato: %s", csv_path)
                continue

            _logger.info("Processando %s per XMLID fix", config["file"])
            with open(csv_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    xml_id = row.get("id")
                    search_value = row.get(config["csv_field"])

                    if not xml_id or not search_value:
                        continue

                    # Cerchiamo il record per il campo specificato
                    record = self.env[config["model"]].search(
                        [(config["search_field"], "=", search_value)], limit=1
                    )

                    if record:
                        full_xml_id = f"l10n_it.{xml_id}"
                        existing_xmlid = self.env.ref(
                            full_xml_id, raise_if_not_found=False
                        )

                        if not existing_xmlid:
                            _logger.info(
                                "Assegnazione XMLID %s a %s (%s: %s)",
                                full_xml_id,
                                config["model"],
                                config["search_field"],
                                search_value,
                            )
                            self.env["ir.model.data"].create(
                                {
                                    "name": xml_id,
                                    "module": "l10n_it",
                                    "model": config["model"],
                                    "res_id": record.id,
                                    "noupdate": True,
                                }
                            )
                        elif existing_xmlid != record:
                            _logger.warning(
                                "XMLID %s già esistente per %s ma punta a "
                                "un altro record (%s invece di %s)",
                                full_xml_id,
                                config["model"],
                                existing_xmlid.id,
                                record.id,
                            )

        # Gestione dei journal standard di Odoo creati da account.chart.template
        # In Odoo 18 i journal standard sono sale, purchase, general, exch,
        # caba, bank, cash, stj. Durante l'installazione di l10n_it,
        # se esistono già, l'installer cerca di riconoscerli tramite XMLID.
        # In Odoo 18 l'XMLID previsto è account.IDCOMPAGNIA_XMLID.
        journals_to_fix = [
            {"xml_id": "sale", "type": "sale", "codes": ["FATT", "INV"]},
            {"xml_id": "purchase", "type": "purchase", "codes": ["ACQ", "BILL"]},
            {"xml_id": "general", "type": "general", "codes": ["VARIE", "MISC"]},
            {"xml_id": "exch", "type": "general", "codes": ["CAMBI", "EXCH"]},
            {"xml_id": "caba", "type": "general", "codes": ["CABA"]},
            {"xml_id": "bank", "type": "bank", "codes": ["BNK4", "BANK"]},
            {"xml_id": "cash", "type": "cash", "codes": ["CSH1", "CASH"]},
            {"xml_id": "stj", "type": "general", "codes": ["STJ"]},
        ]

        company_id = self.env.company.id
        for j_conf in journals_to_fix:
            # Cerchiamo un journal esistente per codice o per tipo
            journal = self.env["account.journal"].search(
                [
                    ("code", "in", j_conf["codes"]),
                    ("company_id", "=", company_id),
                ],
                limit=1,
            )

            if not journal:
                journal = self.env["account.journal"].search(
                    [
                        ("type", "=", j_conf["type"]),
                        ("company_id", "=", company_id),
                    ],
                    limit=1,
                )

            if journal:
                xml_id_name = f"{company_id}_{j_conf['xml_id']}"
                full_xml_id = f"account.{xml_id_name}"
                existing_xmlid = self.env.ref(full_xml_id, raise_if_not_found=False)

                if not existing_xmlid:
                    _logger.info(
                        "Assegnazione XMLID %s al journal %s (tipo: %s)",
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
