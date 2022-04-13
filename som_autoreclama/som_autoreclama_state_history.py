# -*- coding: utf-8 -*-
from osv import osv, fields
from tools.translate import _
from datetime import date

class SomAutoreclamaStateHistory(osv.osv):

    _name = 'som.autoreclama.state.history'

    def get_this_model(self, cursor, uid, context=None):
        return self.pool.get('som.autoreclama.state.history.{}'.format(self._namespace))

SomAutoreclamaStateHistory()


class SomAutoreclamaStateHistoryAtc(SomAutoreclamaStateHistory):

    _name = 'som.autoreclama.state.history.atc'
    _namespace = 'atc'

    def historize(self, cursor, uid, atc_id, next_state_id, current_date, context):
        if not current_date:
            current_date = date.today().strftime("%Y-%m-%d")

        h_ids = self.search(cursor, uid, [
            ('atc_id', '=', atc_id),
            ('end_date', '=', False),
            ],
            context=context
        )
        if h_ids:
            self.write(cursor, uid, h_ids,
                {'end_date': current_date},
                context=context
            )

        return self.create(cursor, uid,
            {
                'atc_id': atc_id,
                'autoreclama_state_id': next_state_id,
                'change_date': current_date,
                'end_date': False,
            },
            context=context
        )


    _columns = {
        'autoreclama_state_id': fields.many2one(
            'som.autoreclama.state',
            u'State',
            required=False
        ),
        'change_date': fields.date(
            u'Change Date',
            select=True,
            readonly=True
        ),
        'end_date': fields.date(
            u'End Date',
            select=True,
            readonly=True
        ),
        'atc_id': fields.many2one(
            'giscedata.atc',
            u'ATC',
            readonly=True,
            ondelete="set null"
        )
    }
    _order = 'end_date desc, id desc'

SomAutoreclamaStateHistoryAtc()
