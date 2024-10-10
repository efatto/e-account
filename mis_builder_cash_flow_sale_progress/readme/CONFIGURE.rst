Configure Mis Builder Report as usual.

In Setting > Configuration > System Parameter add a parameter with:

#. key: mis_builder_cash_flow_sale_progress.valid_states
#. value: a list with state for which cashflow sale lines will be computed, e.g. ["sale", "sent"]

If not configured, default is ["sale"].

