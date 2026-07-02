Un esempio di configurazione nel campo per il nome da assegnare alla sezione:

.. code-block:: python

  ('DDT ' + (object.name or '') + ' - ' + (object.date and object.date.strftime('%d/%m/%Y' or '') + ' ' + (object.sale_ids and ', '.join(x.client_order_ref for x in object.sale_ids) or '') + '.') if object._name == 'stock.delivery.note' else ((object.name or '') + ' - ' + (object.date_order and object.date_order.strftime('%d/%m/%Y') or '') + ' - ' + (object.client_order_ref or '') + '.'))

Un esempio senza DDT sarebbe invece:

.. code-block:: python

  'Ref. ' + object.name + ' - ' + object.date_order.strftime('%d/%m/%Y') + ' - ' + (object.client_order_ref or '') + '. ' + (object.note or '')
