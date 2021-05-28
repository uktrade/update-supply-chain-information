import debug_toolbar

from config.urls import *

urlpatterns += [
    path("__debug__/", include(debug_toolbar.urls)),
]
