import requests
import urllib3
import json
import base64

from config import Config
from cli import log


def http_request(url, cred, headers={}, data=None, method='get',
                 token=None, cookie=None):

    https = Config.HTTPS
    timeout = Config.HTTP_TIMEOUT
    verify_ssl = Config.VERIFY_SSL
    host = cred.get('pc_host')
    port = cred.get('pc_port')
    username = cred.get('username')
    password = cred.get('password')

    if https:
        url = 'https://{}:{}/{}'.format(host, port, url)
    else:
        url = 'http://{}:{}/{}'.format(host, port, url)

    if https and not verify_ssl:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    if token:
        headers['Authorization'] = 'Bearer {}'.format(token)

    elif cookie:
        headers['Set-Cookie'] = '{}={}'.format(cookie.name, cookie.value)

    else:
        auth_str = '{}:{}'.format(username, password)
        base64_str = base64.encodebytes(auth_str.encode()).decode().replace('\n', '')
        headers['Authorization'] = 'Basic {}'.format(base64_str)

    try:
        # https requests apply verify_ssl option
        if https:
            if method.lower() == 'get':
                response = requests.get(url, headers=headers, timeout=timeout, verify=verify_ssl)
            elif method.lower() == 'delete':
                response = requests.delete(url, headers=headers, timeout=timeout, verify=verify_ssl)
            elif method.lower() == 'post':
                response = requests.post(url, data=json.dumps(data), headers=headers, timeout=timeout,
                                         verify=verify_ssl)
            else:
                response = None
        else:
            # http request, so remove verify_ssl option else error is raised by requests lib
            if method.lower() == 'get':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method.lower() == 'post':
                response = requests.post(url, data=json.dumps(data), headers=headers, timeout=timeout)
            else:
                response = None
    except requests.ConnectTimeout:
        log('Connection time out while connecting to {}. Please check connectivity with backend'.format(url))
        return False
    except requests.ConnectionError:
        log('Connection error while connecting to {}. Please check connectivity with backend.'.format(url))
        return False
    except requests.HTTPError:
        log('Connection error while connecting to {}. Please check connectivity with backend.'.format(url))
        return False
    except Exception as error:
        log('An unexpected error while connecting to {} - Exception: {}'.format(url, error.__class__.__name__))
        return False

    return response


def get_vms(cred):
    vms = []

    api_result = http_request('PrismGateway/services/rest/v2.0/vms/', cred)

    if api_result:
        vm_list = json.loads(api_result.content)
        for vm in vm_list['entities']:
            vms.append({'uuid': vm['uuid'],
                        'name': vm['name'],
                        'power_state': True if vm['power_state'] == 'on' else False,
                        'vcpu': int(vm['num_vcpus']),
                        'core': int(vm['num_cores_per_vcpu']),
                        'memory': int(vm['memory_mb'])
                        })
    return vms


def change_power_state(cred, uuid):

    api_result = http_request('PrismGateway/services/rest/v2.0/vms/{}'.format(uuid), cred)
    if api_result:
        vm = json.loads(api_result.content)

        if vm['power_state'].lower() == 'on':
            data = {'uuid': uuid, 'transition': 'OFF'}
            api_result = http_request('PrismGateway/services/rest/v2.0/vms/{}/set_power_state'.format(uuid), cred,
                                      method='POST', data=data)
            if api_result.status_code == 201:
                log('Powering off {} ...\n'.format(vm['name']), color='blue')
            else:
                log('Error changing the power state\n')
        else:
            data = {'uuid': uuid, 'transition': 'ON'}
            api_result = http_request('PrismGateway/services/rest/v2.0/vms/{}/set_power_state'.format(uuid), cred,
                                      method='POST', data=data)
            if api_result.status_code == 201:
                log('Powering on {} ...\n'.format(vm['name']), color='blue')
            else:
                log('Error changing the power state\n')


def clone_vm(cred, uuid, count):
    api_result = http_request('PrismGateway/services/rest/v2.0/vms/{}'.format(uuid), cred)
    if api_result:
        vm = json.loads(api_result.content)
        for clone in range(count):
            clone_name = vm['name'] + ' - Clone {}'.format(clone+1)
            data = {
                'uuid': uuid,
                'spec_list': [{'name': clone_name}]
            }
            clone_result = http_request('PrismGateway/services/rest/v2.0/vms/{}/clone'.format(uuid), cred,
                                        method='POST', data=data)
            if clone_result.status_code == 201:
                log('Creating {}'.format(clone_name), color='blue')
            else:
                log('Error in creating clone\n')

        log('Cloning completed ...\n', color='blue')


def delete_vm(cred, uuid):
    api_result = http_request('PrismGateway/services/rest/v2.0/vms/{}'.format(uuid), cred, method='delete')
    if api_result:
        if api_result.status_code == 201:
            log('Deleting VM ...\n', color='blue')
        else:
            log('Error deleting the VM ...\n')
    else:
        log('Error deleting the VM ...\n')