from db.init_db import init_db
from db.models import Server, AppSetting

def get_setting(key, default=None):
    session = init_db()
    setting = session.query(AppSetting).filter_by(key=key).first()
    value = setting.value if setting else default
    session.close()
    return value

def set_setting(key, value):
    session = init_db()
    setting = session.query(AppSetting).filter_by(key=key).first()
    if setting:
        setting.value = value
    else:
        setting = AppSetting(key=key, value=value)
        session.add(setting)
    session.commit()
    session.close()
