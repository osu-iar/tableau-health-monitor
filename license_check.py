# Checks license info for all existing Tableau licenses. Reports that a license will soon expire if the license has less
# than one month remaining. -v flag can be used to see detailed information about all existing licenses.

import requests
import logging
import time

log = logging.getLogger('TableauHealthMonitor')


def get_license_info(BASE_URL: str, session: requests.Session) -> dict:
    response = session.get(url=f"{BASE_URL}/licensing/productKeys")
    licenses = response.json()
    return licenses


def parse_license_info(verboseFlag: bool, licenses: dict) -> int:
    current_unix = int(time.time()) + 14400  # current time UNIX, add offset for ZULU
    for item in licenses['productKeys']['items']:
        if verboseFlag:
            log.info("[VERBOSE] License: " + item['serial'])
            log.info("[VERBOSE] Expires: " + item['expiration'])
        strippedDate = str(item['expiration'][0:10])

        if strippedDate != "permanent":
            expiry_time_unix = time.mktime(time.strptime(strippedDate, '%Y-%m-%d')) + 14400  # expiry time UNIX + offset
            if expiry_time_unix - current_unix < 2417600:
                log.warning("License " + item['serial'] + " expires in less than 1 month. (Expires " + item
                ['expiration'] + ")")
            else:
                log.info("License Status: no licenses expire within 1 month.")
    return 0
