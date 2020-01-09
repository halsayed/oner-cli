import six
from pyfiglet import figlet_format
from termcolor import colored
from inquirer import prompt, Text, List, errors, Confirm, Password
from inquirer.themes import GreenPassion
from tabulate import tabulate
from config import Config
from colorama import Fore


def log(string, color='red', font="slant", figlet=False):
    if colored:
        if not figlet:
            six.print_(colored(string, color))
        else:
            six.print_(colored(figlet_format(
                string, font=font), color))
    else:
        six.print_(string)


def get_credentials():
    questions = []
    answers = []

    if not Config.PC_HOST:
        questions.append(Text(name='pc_host', message='IP address or host name of Prism Element',
                              validate=input_required))
    else:
        answers.append({'pc_host': Config.PC_HOST})

    if not Config.PC_PORT:
        questions.append(Text(name='pc_port', message='HTTPS port for Prism Element', default='9440',
                              validate=input_required))
    else:
        answers.append({'pc_port': Config.PC_PORT})

    if not Config.USERNAME:
        questions.append(Text(name='username', message='Prism Element username',
                              validate=input_required))
    else:
        answers.append({'username': Config.USERNAME})

    if not Config.PASSWORD:
        questions.append(Password(name='password', message='Password for Prism Element',
                                  validate=input_required))
    else:
        answers.append({'password': Config.PASSWORD})

    answers.append(prompt(questions, theme=GreenPassion()))
    cred = {}
    for answer in answers:
        for key, value in answer.items():
            cred[key] = value

    return cred


def input_required(answers, current):
    if not current:
        raise errors.ValidationError('', reason='This field is required')
    return True


def get_operation():
    operations = [('List VMs', 'list'),
                  ('Change power state of VM', 'power'),
                  ('Delete a VM', 'delete'),
                  ('Clone a VM', 'clone'),
                  ('Exit', 'exit')]
    questions = [
        List('operation',
             message='Select an operation',
             choices=operations, carousel=True)
    ]

    answers = prompt(questions, theme=GreenPassion())
    return answers


def print_vms(vms):
    log('============ VM list from Prism Element (Green: On, Red: Off) ============', color='blue')
    log('==========================================================================', color='blue')
    count = 1
    table = []
    for vm in vms:
        if vm['power_state']:
            color = Fore.GREEN
        else:
            color = Fore.RED

        table.append([
            color + str(count),
            color + vm['name'],
            color + str(vm['vcpu']),
            color + str(vm['core']),
            color + str(vm['memory'])
        ])
        count += 1

    log(tabulate(table, headers=['No', 'Name', 'vCPU', 'Cores', 'Memory'], tablefmt='presto'), color='blue')
    print("\n")


def select_vm(vms, message='Select a VM'):
    vm_list = []
    for vm in vms:
        vm_list.append((vm['name'], vm['uuid']))

    questions = [
        List('uuid',
             message=message,
             choices=vm_list, carousel=True)
    ]
    answers = prompt(questions, theme=GreenPassion())
    return answers


def select_vm_clone(vms):
    answers = select_vm(vms, 'Select a VM to clone')

    questions = [
        Text(name='count', message='Number of clones', validate=clone_count)
    ]

    answers.update(prompt(questions, theme=GreenPassion()))
    return answers


def clone_count(answers, current):
    if int(current) not in range(1, 11):
        raise errors.ValidationError('', reason='Number of clones should be between 1 and 10')
    return True


def select_vm_delete(vms):
    answers = select_vm(vms, 'Select a VM to delete')
    questions = [Confirm('confirm', message="Should I continue")]

    answers.update(prompt(questions, theme=GreenPassion()))
    return answers
