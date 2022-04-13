# -*- coding: utf-8 -*-
from osv import osv, fields
from tools.translate import _
from datetime import date

class GiscedataAtc(osv.osv):

    _name = 'giscedata.atc'
    _inherit = 'giscedata.atc'
    _order = 'id desc'


    def set_autoreclama_history_deactivate(self, cursor, uid, ids, context=None):
        pass




    def get_autoreclama_data(self, cursor, uid, id, context=None):
        data = self.read(cursor, uid, id, ['business_days_with_same_agent','subtipus_id','agent_actual'], context)
        # agent_actual = '10' is ditri
        return {
            'distri_days': data['business_days_with_same_agent'] if data['agent_actual'] == '10' else 0,
            'subtipus_id': data['subtipus_id'][0],
            }


    def update_autoreclama_state(self, cursor, uid, ids, context=None):
        updater_obj = self.pool.get('som.autoreclama.state.updater')
        return updater_obj.update_atcs_if_possible(cursor, uid, ids, context)


    # Automatic ATC + R1-029 from existing ATC / Entry poiut
    def create_related_atc_r1_case_via_wizard(self, cursor, uid, atc_id, context=None):
        channel_obj = self.pool.get('res.partner.canal')
        canal_id = channel_obj.search(cursor, uid, [('name','ilike','intercambi')], context=context)[0]

        subtr_obj = self.pool.get('giscedata.subtipus.reclamacio')
        subtr_id = subtr_obj.search(cursor, uid, [('name','=','029')], context=context)[0]

        atc = self.browse(cursor, uid, atc_id, context)
        new_case_data = {
            'polissa_id': atc.polissa_id.id,
            'descripcio': u'Reclamació per retràs automàtica',
            'canal_id': canal_id,
            'section_id': atc.section_id.id,
            'subtipus_reclamacio_id': subtr_id,
            'comentaris': u'',
            'sense_responsable': True,
            'tanca_al_finalitzar_r1': True,
            'crear_cas_r1': True,
        }
        return self.create_general_atc_r1_case_via_wizard(cursor, uid, new_case_data, context)

    # Automatic ATC + [R1] from dictonary / Entry poiut
    def create_general_atc_r1_case_via_wizard(self, cursor, uid, case_data, context=None):
        ctx = {
            'from_model': 'giscedata.polissa',      # model gas o electricitat
            'polissa_field': 'id',                  # camp per llegir
            'active_ids': [case_data['polissa_id']],# id de la polissa
        }
        params = {
            'canal_id': case_data['canal_id'],
            'subtipus_id': case_data['subtipus_reclamacio_id'],
            'comments': case_data['comentaris'],
            'multi': False,
            'name': case_data['descripcio'],
            'section_id': case_data['section_id'],
            'open_case': True,
            'no_responsible': case_data.get('sense_responsable', False),
            'tancar_cac_al_finalitzar_r1': case_data.get('tanca_al_finalitzar_r1', False),
        }

        atcw_obj = self.pool.get('wizard.create.atc.from.polissa')
        wiz_id = atcw_obj.create(cursor, uid, params, ctx)
        atcw_obj.create_atc_case_from_view(cursor, uid, [wiz_id], ctx)  # creates the ATC case

        gen_cases = atcw_obj.read(cursor, uid, wiz_id, ['generated_cases'], ctx)[0]
        atc_id = gen_cases['generated_cases'][0]                        # gets the new ATC case id

        if case_data.get('crear_cas_r1', False):
            open_r1_wiz = atcw_obj.open_r1_wizard(cursor, uid, [wiz_id], ctx)

            r1atcw_ctx = open_r1_wiz['context']
            r1atcw_obj = self.pool.get(open_r1_wiz['res_model']) # wizard.generate.r1.from.atc.case
            r1atcw_id = r1atcw_obj.create(cursor, uid, {}, r1atcw_ctx)
            generate_r1_wiz = r1atcw_obj.generate_r1(cursor, uid, [r1atcw_id], r1atcw_ctx) #Generates the R1 for the ATC case

            r1w_ctx = eval(generate_r1_wiz['context'])
            r1w_obj = self.pool.get(generate_r1_wiz['res_model']) # "wizard.create.r1"
            r1w_id = r1w_obj.create(cursor, uid, {}, r1w_ctx)
            subtype_r1_wiz = r1w_obj.action_subtype_fields_view(cursor, uid, [r1w_id], r1w_ctx) #obtain subtype wizard R1

            sr1w_ctx = eval(subtype_r1_wiz['context'])
            sr1w_obj = self.pool.get(subtype_r1_wiz['res_model']) # "wizard.subtype.r1"
            sr1w_id = sr1w_obj.create(cursor, uid, {}, sr1w_ctx)
            r1_result = sr1w_obj.action_create_r1_case(cursor, uid, [sr1w_id], sr1w_ctx) #create subtype R1 for example:029

            atr_id = r1_result['domain'][0][2]
            atr_model = r1_result.get('res_model','giscedata.switching')

            r1_to_atc_ref = '{},{}'.format(atr_model, atr_id)
            self.write(cursor, uid, atc_id, {'ref': r1_to_atc_ref}) # link the ATc case with the newly generated R1

            atc_to_r1_ref = '{},{}'.format('giscedata.atc', atc_id)
            atr_obj = self.pool.get(atr_model)
            atr_obj.write(cursor, uid, atr_id, {'ref': atc_to_r1_ref}) # link the R1 with the atc

        return atc_id


    # Create and setup autoreclama history to the new created ATC object
    def create(self, cursor, uid, vals, context=None):
        atc_id = super(GiscedataAtc, self).create(cursor, uid, vals, context=context)
        imd_obj = self.pool.get('ir.model.data')
        correct_state_id = imd_obj.get_object_reference(
                cursor, uid, 'som_autoreclama', 'correct_state_workflow_atc'
        )[1]

        atch_obj = self.pool.get('som.autoreclama.state.history.atc')
        atch_obj.create(
            cursor,
            uid,
            {
                'atc_id': atc_id,
                'autoreclama_state_id': correct_state_id,
                'change_date': date.today().strftime("%d-%m-%Y"),
            }
        )
        return atc_id

    # Autoreclama history management functions
    def get_current_autoreclama_state_info(self, cursor, uid, ids, context=None):
        """
            Get the info of the last history line by atc id.
        :return: a dict containing the info of the last history line of the
                 atc indexed by its id.
                 ==== Fields of the dict for each atc ===
                 'id': if of the last som.autoreclama.state.history.atc
                 'autoreclama_state_id': id of its state
                 'change_date': date of change (also, date of the creation of
                                the line)
        """
        if context is None:
            context = {}
        if not isinstance(ids, list):
            ids = [ids]
        history_obj = self.pool.get('som.autoreclama.state.history.atc')
        result = dict.fromkeys(ids, False)
        fields_to_read = ['autoreclama_state_id', 'change_date', 'atc_id']
        for id in ids:
            res = history_obj.search(
                cursor, uid, [('atc_id', '=', id)]
            )
            if res:
                # We consider the last record the first one due to order
                # statement in the model definition.
                values = history_obj.read(
                    cursor, uid, res[0], fields_to_read)
                result[id] = {
                    'id': values['id'],
                    'autoreclama_state_id': values['autoreclama_state_id'][0],
                    'change_date': values['change_date'],
                }
            else:
                result[id] = False
        return result

    # Autoreclama history management functions
    def _get_last_autoreclama_state_from_history(self, cursor, uid, ids, field_name, arg, context=None):
        result = {k: {} for k in ids}
        last_lines = self.get_current_autoreclama_state_info(cursor, uid, ids)
        for id in ids:
            if last_lines[id]:
                result[id]['autoreclama_state'] = last_lines[id]['autoreclama_state_id']
                result[id]['autoreclama_state_date'] = last_lines[id]['change_date']
            else:
                result[id]['autoreclama_state'] = False
                result[id]['autoreclama_state_date'] = False
        return result

    # Autoreclama history management functions
    def change_state(self, cursor, uid, ids, context):
        values = self.read(cursor, uid, ids, ['atc_id'])
        return [value['atc_id'][0] for value in values]

    _STORE_STATE = {
        'som.autoreclama.state.history.atc': (
            change_state, ['change_date'], 10
        )
    }

    _columns = {
        'autoreclama_state': fields.function(
            _get_last_autoreclama_state_from_history,
            method=True,
            type='many2one',
            obj='som.autoreclama.state',
            string=_(u'Estat autoreclama'),
            required=False,
            readonly=True,
            store=_STORE_STATE,
            multi='autoreclama'
        ),
        'autoreclama_state_date': fields.function(
            _get_last_autoreclama_state_from_history,
            method=True,
            type='date',
            string=_(u"última data d'autoreclama"),
            required=False,
            readonly=True,
            store=_STORE_STATE,
            multi='autoreclama'
        ),
        'autoreclama_history_ids': fields.one2many(
            'som.autoreclama.state.history.atc',
            'atc_id',
            _(u"Historic d'autoreclama"),
            readonly=True
        ),
    }

GiscedataAtc()
