from datetime import datetime
import ssl
import socket

from django.utils.timezone import get_current_timezone


def ssl_info(domain):
    try:
        context = ssl.create_default_context()
        with (
            socket.create_connection((domain, 443)) as sock,
            context.wrap_socket(sock, server_hostname=domain) as ssock
        ):
                cert = ssock.getpeercert()
                issue_date = cert['notBefore']
                expiry_date = cert['notAfter']
                gmt_timezone = get_current_timezone()
                return (
                    datetime.strptime(str(issue_date), "%b %d %H:%M:%S %Y %Z").replace(tzinfo=gmt_timezone),
                    datetime.strptime(str(expiry_date), "%b %d %H:%M:%S %Y %Z").replace(tzinfo=gmt_timezone)
                )
    except (OSError, ssl.SSLError, ConnectionError):
        return None, None
