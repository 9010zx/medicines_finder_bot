class EmptyFormException(Exception):
    pass

class EmptyDataException(Exception):
    pass

async def drug_name_filter(raw_msg):
    msg = str(raw_msg)
    if len(msg) < 3 or len(msg) > 30:
        return None
    else:
        return msg    
