This module is used to prevent duplication of accounting accounts during
the installation of the Italian localization module (`l10n_it`).

Before the module is installed, a `pre_init_hook` is executed which:
1. Reads the CSV files (`account.account-it.csv`, `account.tax-it.csv`,
   `account.tax.group-it.csv`, `account.fiscal.position-it.csv`) from the
   `l10n_it` module.
2. Searches the database for existing records that match the data defined
   in the CSVs (by code or name).
3. Handles standard Odoo journals (`sale`, `purchase`, `general`,
   `exch`, `caba`, `bank`, `cash`, `stj`) by assigning them the standard
   Odoo 18 XMLID (`account.COMPANYID_XMLID`) if not already present.
4. If it finds a match for accounts, taxes or fiscal positions and the record
   does not yet have an XMLID for the `l10n_it` module, it assigns it.

In this way, when `l10n_it` is installed or loaded, Odoo will recognize
the existing records via the XMLID and update them instead of creating
new duplicates.
