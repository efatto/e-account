# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp


class AccountVatPeriodEndStatement(orm.Model):
    _inherit = "account.vat.period.end.statement"

    def _get_endyear_periods(self, cr, uid, ids, name, args, context=None):
        result = {}
        periods = []
        for statement in self.browse(cr, uid, ids, context=context):
            for statement_child in statement.statement_ids:
                for period in statement_child.period_ids:
                    periods.append(period.id)
            result[statement.id] = periods
        return result

    def onchange_endyear_statement(
            self, cr, uid, ids, endyear_statement, context=None):
        if endyear_statement:
            return {
                'value': {
                    'interest': False,
                }
            }

    _columns = {
        'endyear_statement': fields.boolean('End of year statement'),
        'endyear_statement_id': fields.many2one(
            'account.vat.period.end.statement',
            'End of year Statement parent'),
        'statement_ids': fields.one2many(
            'account.vat.period.end.statement',
            'endyear_statement_id', 'End of year Statement childs'),
        'endyear_period_ids': fields.function(
            _get_endyear_periods, relation='account.period',
            type="many2many", string='End of year periods'),
        'based_on_dates': fields.boolean(string='Based on dates'),
        'date_start': fields.date(string='Start Date'),
        'date_end': fields.date(string='End Date'),
    }

    def add_periods(self, cr, uid, ids, context=None):
        for statement in self.browse(cr, uid, ids, context):
            st_date = statement.date
            fiscalyears = self.pool.get('account.fiscalyear').search(
                cr, uid, [
                    ('date_start', '<=', st_date),
                    ('date_stop', '>=', st_date)], limit=1)
            fiscalyear = self.pool.get('account.fiscalyear').browse(
                cr, uid, fiscalyears[0])
            period_obj = self.pool.get('account.period')
            periods = period_obj.search(
                cr, uid, [
                    ('special', '=', False,),
                    ('fiscalyear_id', '=', fiscalyear.id)])
            statements = self.search(cr, uid, [('period_ids', 'in', periods)])
            for statement_child in self.browse(cr, uid, statements, context):
                statement_child.write({'endyear_statement_id': statement.id})
            statement.compute_amounts(context=context)
        return True

    def compute_amounts(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        statement_generic_account_line_obj = self.pool[
            'statement.generic.account.line']
        decimal_precision_obj = self.pool['decimal.precision']
        debit_line_pool = self.pool.get('statement.debit.account.line')
        credit_line_pool = self.pool.get('statement.credit.account.line')
        for statement in self.browse(cr, uid, ids, context):
            statement.write({'previous_debit_vat_amount': 0.0})
            prev_statement_ids = self.search(
                cr, uid, [('date', '<', statement.date)], order='date')
            if prev_statement_ids:
                prev_statement = self.browse(
                    cr, uid, prev_statement_ids[len(prev_statement_ids) - 1],
                    context)
                if (
                    prev_statement.residual > 0 and
                    prev_statement.authority_vat_amount > 0
                ):
                    statement.write(
                        {'previous_debit_vat_amount': prev_statement.residual})
                elif prev_statement.authority_vat_amount < 0:
                    statement.write(
                        {'previous_credit_vat_amount': (
                            - prev_statement.authority_vat_amount)})

            credit_line_ids = []
            debit_line_ids = []
            tax_code_pool = self.pool.get('account.tax.code')
            debit_tax_code_ids = tax_code_pool.search(cr, uid, [
                ('vat_statement_account_id', '!=', False),
                ('exclude_from_registries', '!=', True),
                ('vat_statement_type', '=', 'debit'),
            ], context=context)
            for debit_tax_code_id in debit_tax_code_ids:
                debit_tax_code = tax_code_pool.browse(
                    cr, uid, debit_tax_code_id, context)
                total = total_base = 0.0
                # changed for total vat
                periods = []
                if statement.endyear_statement and statement.statement_ids:
                    for statement_child in statement.statement_ids:
                        periods += statement_child.period_ids
                else:
                    periods = statement.period_ids
                if statement.based_on_dates:
                    ctx = context.copy()
                    ctx['date_start'] = statement.date_start
                    ctx['date_end'] = statement.date_end
                    total += tax_code_pool.browse(
                        cr, uid, debit_tax_code_id, ctx).sum_date
                else:
                    for period in periods:
                        ctx = context.copy()
                        ctx['period_id'] = period.id
                        total += tax_code_pool.browse(
                            cr, uid, debit_tax_code_id, ctx).sum_period
                        #  get total from periods for base amount
                        res = tax_code_pool._get_tax_codes_amounts(
                            cr, uid, period.id, tax_code_ids=debit_tax_code.id)
                        total_base += sum(res[a]['base'] for a in res)

                debit_line_ids.append({
                    'account_id': debit_tax_code.vat_statement_account_id.id,
                    'tax_code_id': debit_tax_code.id,
                    'amount': not debit_tax_code.is_base and total *
                    debit_tax_code.vat_statement_sign or 0.0,
                    'amount_base': debit_tax_code.is_base and total *
                    debit_tax_code.vat_statement_sign or total_base *
                    debit_tax_code.vat_statement_sign, })

            credit_tax_code_ids = tax_code_pool.search(cr, uid, [
                ('vat_statement_account_id', '!=', False),
                ('exclude_from_registries', '!=', True),
                ('vat_statement_type', '=', 'credit'),
            ], context=context)
            for credit_tax_code_id in credit_tax_code_ids:
                credit_tax_code = tax_code_pool.browse(
                    cr, uid, credit_tax_code_id, context)
                total = total_base = 0.0
                # changed for total vat
                periods = []
                if statement.endyear_statement and statement.statement_ids:
                    for statement_child in statement.statement_ids:
                        periods += statement_child.period_ids
                else:
                    periods = statement.period_ids
                if statement.based_on_dates:
                    ctx = context.copy()
                    ctx['date_start'] = statement.date_start
                    ctx['date_end'] = statement.date_end
                    total += tax_code_pool.browse(
                        cr, uid, credit_tax_code_id, ctx).sum_date
                else:
                    for period in periods:
                        # for period in statement.period_ids:
                        ctx = context.copy()
                        ctx['period_id'] = period.id
                        total += tax_code_pool.browse(
                            cr, uid, credit_tax_code_id, ctx).sum_period
                        #  get total from periods for base amount
                        res = tax_code_pool._get_tax_codes_amounts(
                            cr, uid, period.id,
                            tax_code_ids=credit_tax_code.id)
                        total_base += sum(res[a]['base'] for a in res)

                credit_line_ids.append({
                    'account_id': credit_tax_code.vat_statement_account_id.id,
                    'tax_code_id': credit_tax_code.id,
                    'amount': not credit_tax_code.is_base and total *
                    credit_tax_code.vat_statement_sign or 0.0,
                    'amount_base': credit_tax_code.is_base and total *
                    credit_tax_code.vat_statement_sign or total_base *
                    credit_tax_code.vat_statement_sign, })

            for debit_line in statement.debit_vat_account_line_ids:
                debit_line.unlink()
            for credit_line in statement.credit_vat_account_line_ids:
                credit_line.unlink()
            for debit_vals in debit_line_ids:
                debit_vals.update({'statement_id': statement.id})
                debit_line_pool.create(cr, uid, debit_vals, context=context)
            for credit_vals in credit_line_ids:
                credit_vals.update({'statement_id': statement.id})
                credit_line_pool.create(cr, uid, credit_vals, context=context)

            interest_amount = 0.0
            # if exits Delete line with interest
            acc_id = self.get_account_interest(cr, uid, ids, context)
            domain = [
                ('account_id', '=', acc_id),
                ('statement_id', '=', statement.id),
                ]
            line_ids = statement_generic_account_line_obj.search(
                cr, uid, domain)
            if line_ids:
                statement_generic_account_line_obj.unlink(cr, uid, line_ids)

            # Compute interest
            if statement.interest and statement.authority_vat_amount > 0:
                interest_amount = (-1 * round(
                    statement.authority_vat_amount *
                    (float(statement.interest_percent) / 100),
                    decimal_precision_obj.precision_get(cr, uid, 'Account')))
            # Add line with interest
            if interest_amount:
                val = {
                    'statement_id': statement.id,
                    'account_id': acc_id,
                    'amount': interest_amount,
                    }
                statement_generic_account_line_obj.create(cr, uid, val)
        return True


class StatementDebitAccountLine(orm.Model):
    _inherit = 'statement.debit.account.line'
    _columns = {
        'amount_base': fields.float(
            'Amount base', digits=dp.get_precision('Account')),
    }


class StatementCreditAccountLine(orm.Model):
    _inherit = 'statement.credit.account.line'
    _columns = {
        'amount_base': fields.float(
            'Amount base', digits=dp.get_precision('Account')),
    }


class AccountTaxCode(orm.Model):
    _inherit = 'account.tax.code'

    def _sum_dates(self, cr, uid, ids, name, args, context, where='',
                   where_params=()):
        parent_ids = tuple(self.search(
            cr, uid, [('parent_id', 'child_of', ids)]))
        cr.execute('SELECT line.tax_code_id, sum(line.tax_amount) \
                FROM account_move_line AS line, \
                account_move AS move \
                WHERE line.tax_code_id IN %s '+where+' \
                AND move.id = line.move_id \
                GROUP BY line.tax_code_id',
                   (parent_ids,) + where_params)
        res = dict(cr.fetchall())
        obj_precision = self.pool.get('decimal.precision')
        res2 = {}
        for record in self.browse(cr, uid, ids, context=context):
            def _rec_get(record):
                amount = res.get(record.id) or 0.0
                for rec in record.child_ids:
                    amount += _rec_get(rec) * rec.sign
                return amount
            res2[record.id] = round(
                _rec_get(record), obj_precision.precision_get(
                    cr, uid, 'Account'))
        return res2

    def _sum_date(self, cr, uid, ids, name, args, context):
        if context is None:
            context = {}
        move_state = ('posted', )
        if context.get('state', False) == 'all':
            move_state = ('draft', 'posted', )
        if context.get('date_start', False):
            date_start = context['date_start']
        if context.get('date_end', False):
            date_end = context['date_end']
        if date_start and date_end:
            return self._sum_dates(
                cr, uid, ids, name, args, context, where=' AND line.date>=%s '
                'AND line.date<=%s AND move.state IN %s',
                where_params=(date_start, date_end, move_state))
        else:
            return False

    _columns = {
        'sum_date': fields.function(_sum_date, string="Period Sum"),
    }
