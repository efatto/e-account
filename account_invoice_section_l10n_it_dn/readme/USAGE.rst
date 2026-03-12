Un esempio di configurazione nel campo per il nome da assegnare alla sezione:

.. code-block:: python

  ('DDT ' + (object.name or '') + ' - ' + (object.date and object.date.strftime('%d/%m/%Y' or '') + '.') if object._name == 'stock.delivery.note' else ((object.name or '') + ' - ' + (object.date_order and object.date_order.strftime('%d/%m/%Y') or '') + ' - ' + (object.client_order_ref or '') + '.'))
