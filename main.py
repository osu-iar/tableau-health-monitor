import requests
import pymsteams
import json
import os
import sys
import logging

from dotenv import load_dotenv

load_dotenv()

# Setup Logger
log = logging.getLogger('TableauHealthMonitor')
log.setLevel(logging.INFO)

logging_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ch = logging.StreamHandler()
ch.setFormatter(logging_format)

fh = logging.FileHandler(filename='tabhealth.log', mode='a', encoding='utf-8')
fh.setFormatter(logging_format)

log.addHandler(ch)
log.addHandler(fh)

TABLEAU_URL = 'https://tableau-test-01.iar.oregonstate.edu'
TSM_PORT    = '8850'
BASE_URL    = f'{TABLEAU_URL}:{TSM_PORT}/api/0.5'

HEADERS = {
    'content-type': 'application/json'
}

AUTH_PAYLOAD = {
    'authentication': {
        'name': os.getenv('tabhealth_username')
        , 'password': os.getenv('tabhealth_password')
    }
}


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
    request = session.post(url=f'{BASE_URL}/login', data=json.dumps(AUTH_PAYLOAD), headers=HEADERS)
    if request.status_code != 204:
        log.critical('Could not login to TSM API. Login Status: %s', request.status_code)
        sys.exit(1)


def logout_of_api(session: requests.Session) -> None:
    request = session.post(url=f'{BASE_URL}/logout')
    if request.status_code != 200:
        log.warning('Could not logout of TSM API. Logout Status: %s', request.status_code)


def get_server_status(session: requests.Session) -> requests.Request:
    request = session.get(url=f"{BASE_URL}/status")
    if request.status_code != 200:
        log.critical('Could not retrieve server status. Status Code: %s', request.status_code)
        sys.exit(1)

    return request


def check_node_status(node_name:str, services: dict) -> None:
    # this is a disabled service. We don't care.
    for service in services:
        if service['rollupRequestedDeploymentState'] == 'Disabled':
            log.debug('%s: %s is disabled. Skipping', node_name, service['serviceName'])
        elif service['rollupRequestedDeploymentState'] == 'Enabled':
            if service['rollupStatus'] != 'Running':
                log.warning('%s: %s is enabled, but has a status of %s',
                            node_name, service['serviceName'], service['rollupStatus'])
            else:
                log.debug('%s: %s is running as expected', node_name, service['serviceName'])


def check_server_status(data: dict) -> None:
    if data['clusterStatus']['rollupStatus'] == 'Running':
        log.info('Rollup status: Running')

    for node in data['clusterStatus']['nodes']:
        check_node_status(node['nodeId'], node['services'])


if __name__ == '__main__':
    session = setup_session()

    login_to_api(session)

    server_status: requests.Request = get_server_status(session)

    check_server_status(server_status.json())
    logout_of_api(session)
