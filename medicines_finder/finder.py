import json
import logging
from medicines_finder import exc
from medicines_finder.redis_connect import send_to_redis
import aiogram.utils.markdown as fmt


class Finder:

    def store_recived_msg(self, data):
        self.recived_msg = data

    def prepare_msg(self):
        for i in self.recived_msg[:5]:
            koord = json.dumps([i['map1'], i['map2']])
            msg = fmt.text(
                fmt.text('Название:', i['nmfirm']),
                fmt.text('Адрес:', i['str']),
                fmt.text('Время работы:', i['time']),
                fmt.text('Стоимость:', i['price']),
                sep='\n',
            )
            yield msg, koord 
        

    @staticmethod
    def get_search_dict(drug_name, koord: list):
        raw = {
            "type":"lekar",
            "string":drug_name,
            "input_select":"false",
            "search_settings":{
                "city":["1"],
                "rayon":[],
                "street":[],
                "apteka":[],
                "near":False,
                "krugl":False,
                "geolocation":True,
                "koord":koord,
                }
            }
        return raw

    @staticmethod
    def get_search_dict_lvl_2(cdprep, cdform, koord: list):
        raw = {
            "type":"form_lvl_2",
            "cdprep":cdprep,
            "cdform":cdform,
            "search_settings":{
                "city":["1"],
                "rayon":[],
                "street":[],
                "apteka":[],
                "near":False,
                "krugl":False,
                "geolocation":True,
                "koord":koord,
                }
            }
        return raw
    
def get_drug_forms(forms: list):
    if not forms:
        logging.error('Forms is empty')
        raise exc.EmptyFormException('Forms is empty')
    for form in forms:
        callable_data = form['form'][:30]
        send_to_redis(callable_data, json.dumps(form, ensure_ascii=False))
        yield form['form'], callable_data
