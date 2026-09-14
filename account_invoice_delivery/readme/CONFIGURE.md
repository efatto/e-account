Go to *Settings \> Sales \> Shipping* and enable
"Refresh shipping cost line automatically" for each company that should
automatically add and refresh delivery charges on draft customer invoices,
credit notes and receipts. This is the same company setting used by
`delivery_auto_refresh` for sales orders.

Select a delivery method on the invoice, or create the invoice from a sales
order with a carrier. Fixed-price and rule-based delivery methods are supported.
Invoices containing only services do not receive a delivery line.

Delivery lines are updated in place, retaining their discounts and links to
sales order lines. Orders with different carriers are invoiced separately.
Posted invoices and vendor documents are not refreshed.

Pricing follows Odoo 18 delivery rules, including percentage and fixed margins,
fiscal positions and currency conversion at the invoice date. Amount-based
rules include taxes and service lines, excluding delivery charges. For
rule-based carriers, configure free shipping in the price rules.

Invoice delivery lines use the calculated charge even when the carrier's
invoicing policy is based on actual costs; the zero-price estimate used on
sales quotations is not applied to invoices.
