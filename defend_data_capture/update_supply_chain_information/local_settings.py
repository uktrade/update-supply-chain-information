from update_supply_chain_information.settings import *

ROOT_URLCONF = "defend_data_capture.local_urls"
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
INSTALLED_APPS += ["debug_toolbar"]
INTERNAL_IPS = ["127.0.0.1"]
