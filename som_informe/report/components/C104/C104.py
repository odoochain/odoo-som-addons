from ..component_utils import dateformat
from ..ProcesC1 import ProcesC1

class C104(ProcesC1.ProcesC1):
    def __init__(self):
        ProcesC1.ProcesC1.__init__(self)

    def get_data(self, wiz, cursor, uid, step):
        result = ProcesC1.ProcesC1.get_data(self, wiz, cursor, uid, step)
        result['type'] = 'C104'
        result['data_rebuig'] = dateformat(step.data_rebuig)
        result['rebutjos'] = [{'codi':rebuig.motiu_rebuig.name, 'descripcio' : rebuig.desc_rebuig} for rebuig in step.rebuig_ids]
        return result