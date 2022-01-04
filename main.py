import requests
import json
import os
import sys
import logging
import argparse
import license_check
import status_check
from dotenv import load_dotenv

load_dotenv()

# Set up Logger
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


def setup_parser() -> argparse.ArgumentParser:
    # Set up argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v"
        , "--verbose"
        , help="Report all license expiry dates (must use license arg as well)"
        , action="store_true"
    )

    parser.add_argument(
        "command"
        , help="Use the license argument to check license expiry status."
        , choices=['license', 'health']
        , default='health'
        # , action="store"
        , nargs='?'
    )

    return parser


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


if __name__ == '__main__':
    parser = setup_parser()
    args = parser.parse_args()

    session = setup_session()
    login_to_api(session)

    if args.command == 'license':
        licenses = license_check.get_license_info(BASE_URL, session)
        exit_status = license_check.parse_license_info(args.verbose, licenses)
    elif args.command == 'health':
        server_status: requests.Request = status_check.get_server_status(BASE_URL, session)
        exit_status = status_check.check_server_status(server_status.json())

    logout_of_api(session)
    sys.exit(exit_status)
