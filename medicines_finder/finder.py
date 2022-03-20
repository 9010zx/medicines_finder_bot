import json
from medicines_finder import socketio
from medicines_finder.redis_connect import send_to_redis , get_from_redis
from medicines_finder import exc
import logging
from aiogram.utils import markdown as fmt


class Finder:
    def __init__(self, event, user_id, drug_name):
        self.drug_search_msg = self.__set_drug_search_dict(drug_name)
        self.event = event
        self.forms_redis_key = f'{user_id}_{event}'
        
    async def get_forms(self):
        await socketio.connect_to_allapteki(
            self.event,
            self.drug_search_msg,
            self.forms_redis_key
        )
    def remove_forms_from_redis(self):
        pass

    def __set_drug_search_dict(self,drug_name):
        search_dict = {
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
                "geolocation":False,
                "koord":"",
                }
            }
        return search_dict

    @staticmethod
    async def append_choosen_form(user_id, data):
        logging.info(f'{user_id} request {data}')
        try:
            data_for_send = await get_from_redis(user_id)
        except exc.EmptyDataException:
            await send_to_redis(user_id, [data])
            return
        data_for_send.append(data)
        await send_to_redis(user_id, data_for_send)

    @staticmethod
    async def get_price(user_id, koord:list):
        drugs = await get_from_redis(user_id)
        search_settings = {
                "city":["1"],
                "rayon":[],
                "street":[],
                "apteka":[],
                "near":False,
                "krugl":False,
                "geolocation":True,
                "koord":koord,
        }
        if len(drugs) == 1:
            search_msg = {
                "type":"form_lvl_2",
                "cdprep":drugs[0]['cdprep'],
                "cdform":drugs[0]['cdform'],
                }
            search_msg['search_settings'] = search_settings
            event = 'form_lvl_2'
        else:
            search_msg = {"type":"group",
                "mass_id_lek":[],
                }
            for drug in drugs:
                mass_id = {
                    'cdprep': drug['cdprep'],
                    'cdform': drug['cdform']
                }
                search_msg['mass_id_lek'].append(mass_id)
            search_msg['search_settings'] = search_settings
            event = 'lekarstva_group_seach'
        
        key = f"{user_id}_{event}"
        await socketio.connect_to_allapteki(event, search_msg, key)
        return key

        