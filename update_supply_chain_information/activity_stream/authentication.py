import sys
import traceback

from django.conf import settings
from hawkrest import (
    HawkAuthentication,
    get_auth_header,
    log,
    is_hawk_request,
    seen_nonce,
    default_message_expiration,
)
from mohawk import Receiver
from mohawk.exc import HawkFail, BadHeaderValue, TokenExpired
from rest_framework.exceptions import AuthenticationFailed


class ActivityStreamHawkAuthentication(HawkAuthentication):
    """
    The `authenticate()` method is lifted wholesale from the superclass
    so we can override the content type when the server provides one
    that wasn't actually set by the client, Activity Stream.
    """

    def authenticate(self, request):
        # In case there is an exception, tell others that the view passed
        # through Hawk authorization. The META dict is used because
        # middleware may not get an identical request object.
        # A dot-separated key is to work around potential environ var
        # pollution of META.
        request.META["hawk.receiver"] = None

        http_authorization = get_auth_header(request)
        if not http_authorization:
            log.debug("no authorization header in request")
            return None
        elif not is_hawk_request(request):
            log.debug(
                "ignoring non-Hawk authorization header: {} ".format(http_authorization)
            )
            return None

        content_type = request.META.get("CONTENT_TYPE", "")
        if content_type == "text/plain":
            # This is being set by Python's WSGI server; the request had a blank content type.
            content_type = ""
        try:
            receiver = Receiver(
                lambda cr_id: self.hawk_credentials_lookup(cr_id),
                http_authorization,
                request.build_absolute_uri(),
                request.method,
                content=request.body,
                seen_nonce=(
                    seen_nonce
                    if getattr(settings, "USE_CACHE_FOR_HAWK_NONCE", True)
                    else None
                ),
                content_type=content_type,
                timestamp_skew_in_seconds=getattr(
                    settings, "HAWK_MESSAGE_EXPIRATION", default_message_expiration
                ),
            )
        except HawkFail as e:
            etype, val, tb = sys.exc_info()
            log.debug(traceback.format_exc())
            log.warning(
                "access denied: {etype.__name__}: {val}".format(etype=etype, val=val)
            )
            # The exception message is sent to the client as part of the
            # 401 response, so we're intentionally vague about the original
            # exception type/value, to avoid assisting attackers.
            msg = "Hawk authentication failed"
            if isinstance(e, BadHeaderValue):
                msg += ": The request header was malformed"
            elif isinstance(e, TokenExpired):
                msg += ": The token has expired. Is your system clock correct?"
            raise AuthenticationFailed(msg)

        # Pass our receiver object to the middleware so the request header
        # doesn't need to be parsed again.
        request.META["hawk.receiver"] = receiver
        return self.hawk_user_lookup(request, receiver.resource.credentials)
