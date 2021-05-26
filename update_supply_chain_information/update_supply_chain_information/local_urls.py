import debug_toolbar

from update_supply_chain_information.urls import *

urlpatterns += [
    path("__debug__/", include(debug_toolbar.urls)),
]
