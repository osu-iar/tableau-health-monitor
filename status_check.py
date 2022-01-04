# Checks status/health of the Tableau service.

import requests
import sys
import logging

log = logging.getLogger('TableauHealthMonitor')


def get_server_status(BASE_URL: str, session: requests.Session) -> requests.Request:
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