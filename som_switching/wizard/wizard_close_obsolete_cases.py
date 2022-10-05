# -*- coding: utf-8 -*-
from osv import osv, fields
from tools.translate import _


class WizardCloseObsoleteCases(osv.osv_memory):

    _name = "wizard.close.obsolete.cases"

    def _get_info_default(self, cursor, uid, context=None):
        if not context:
            context = {}
        return _(
            u"Només els casos oberts:\n"
            u" * D1 01 amb motiu 04 amb pólissa de baixa o autoconsum activat\n"
        )

    def close_obsolete_cases(self, cursor, uid, ids, context=None):
        sw_obj = self.pool.get("giscedata.switching")

        if not context:
            context = {}
        wizard = self.browse(cursor, uid, ids[0], context)

        sw_ids = context.get("active_ids", [])

        info = ""
        case_ids = []  # Casos a tancar
        for sw_id in sw_ids:
            sw = sw_obj.browse(cursor, uid, sw_id, context)
            if sw.state != "open":
                continue
            if sw.proces_id.name == "D1" and sw.step_id.name == "01":  # D101
                if sw.step_ids[0].pas_id.motiu_canvi != "04":
                    continue
                if (
                    not sw.cups_polissa_id.active
                    or sw.cups_polissa_id.autoconsumo != "00"
                ):
                    case_ids.append(sw.case_id)

            ctx = context.copy()
            ctx.update({"active_ids": case_ids})
            self.perform_close(cursor, uid, ids, context=ctx)

            # info += "%s: %s\n\n" % (res[0], res[1]) TODO

        wizard.write({"info": info, "state": "done"})

        return

    _columns = {
        "state": fields.char("State", size=16),
        "info": fields.text("Info"),
    }

    _defaults = {
        "state": lambda *a: "init",
        "info": _get_info_default,
    }


WizardCloseObsoleteCases()
