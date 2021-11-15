from sentry_sdk import capture_exception

from healthcheck.constants import HealthStatus
from healthcheck.models import HealthCheck


def db_check():
    """
    Performs a basic check on the database by performing a select query on a simple table
    :return: str "OK" or "FAIL" according to successful retrieval
    """
    try:
        h = HealthCheck.objects.first()
        return HealthStatus.OK
    except Exception as e:
        capture_exception(e)
        return HealthStatus.FAIL
