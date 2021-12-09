import requests
import json
import os
import sys
import logging
import time
import argparse

from dotenv import load_dotenv

load_dotenv()

# Set up argparse
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--license", help="Use the license argument to check license expiry status.", action="store_true")
parser.add_argument("-v", "--verbose", help="Report all license expiry dates (must use license arg as well)", action="store_true")
args = parser.parse_args()

# default (no arg)
healthFlag = True
licenseFlag = False
verboseFlag = False

# set flags based on args
if args.license:
    healthFlag = False
    licenseFlag = True
    if args.verbose:
        verboseFlag = True



# Setup Logger
log = logging.getLogger('TableauHealthMonitor')
log.setLevel(logging.INFO)

logging_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ch = logging.StreamHandler()
ch.setFormatter(logging_format)

fh = logging.FileHandler(filename='tabhealth.log', mode='a', encoding='utf-8')
fh.setFormatter(logging_format)

if os.getenv('tabhealth_console_logging'):
    log.addHandler(ch)

if os.getenv('tabhealth_file_logging'):
    log.addHandler(fh)

TABLEAU_URL = os.getenv('tabhealth_server')
TSM_PORT = os.getenv('tabhealth_port')
BASE_URL = f'{TABLEAU_URL}:{TSM_PORT}/api/0.5'

HEADERS = {
    'content-type': 'application/json'
}

AUTH_PAYLOAD = {
    'authentication': {
        'name': os.getenv('tabhealth_username')
        , 'password': os.getenv('tabhealth_password')
    }
}

EXIT_STATUS = 0


def setup_session() -> requests.Session:
    # Disable the SSL checking as Tableau uses a self-signed cert
    # and it's not important enough to do anything about it here
    session = requests.Session()
    requests.packages.urllib3.disable_warnings()
    session.verify = False

    # We'll want these headers on all calls
    session.headers.update(HEADERS)
    return session


def login_to_api(session: requests.Session) -> None:
    try:
        request = session.post(url=f'{BASE_URL}/login', data=json.dumps(AUTH_PAYLOAD), headers=HEADERS)
        if request.status_code != 204:
            log.critical('Could not login to TSM API. Login Status: %s', request.status_code)
            sys.exit(1)
    except requests.exceptions.InvalidSchema:
        log.critical('Could not determine the web protocal to use. Double check that you included https://.')
        sys.exit(1)


def logout_of_api(session: requests.Session) -> None:
    request = session.post(url=f'{BASE_URL}/logout')
    if request.status_code != 200:
        log.warning('Could not logout of TSM API. Logout Status: %s', request.status_code)


def get_license_info(session: requests.Session) -> dict:
    response = session.get(url=f"{BASE_URL}/licensing/productKeys")
    licenses = response.json()
    return licenses


def parse_license_info(licenses: dict) -> int:
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


def get_server_status(session: requests.Session) -> requests.Request:
    request = session.get(url=f"{BASE_URL}/status")
    if request.status_code != 200:
        log.critical('Could not retrieve server status. Status Code: %s', request.status_code)
        sys.exit(1)

    return request


def check_node_status(node_name: str, services: dict) -> None:
    num_problems = 0

    for service in services:
        if service['rollupRequestedDeploymentState'] == 'Disabled':
            log.info('%s: %s is disabled. Skipping', node_name, service['serviceName'])
        elif service['rollupRequestedDeploymentState'] == 'Enabled':
            if service['rollupStatus'] != 'Running':
                log.critical('%s: %s is enabled, but has a status of %s',
                             node_name, service['serviceName'], service['rollupStatus'])
                num_problems += 1
            else:
                log.info('%s: %s is running as expected', node_name, service['serviceName'])

    return num_problems


def check_server_status(data: dict) -> int:
    num_problems = 0

    if data['clusterStatus']['rollupStatus'] == 'Running':
        log.info('Rollup status: Running')
        return num_problems
    else:
        for node in data['clusterStatus']['nodes']:
            num_problems += check_node_status(node['nodeId'], node['services'])

        return num_problems


if __name__ == '__main__':
    session = setup_session()

    login_to_api(session)

    if licenseFlag:
        licenses = get_license_info(session)
        exit_status = parse_license_info(licenses)

    if healthFlag:
        server_status: requests.Request = get_server_status(session)
        exit_status = check_server_status(server_status.json())

    logout_of_api(session)
    sys.exit(exit_status)
