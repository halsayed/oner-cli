
from prism_api import get_vms, change_power_state, clone_vm, delete_vm
from cli import log, get_credentials, get_operation, print_vms, select_vm_clone, select_vm, select_vm_delete
from config import Config


def main():

    log(Config.APP_TITLE, color='blue', figlet=True)
    log(Config.WELCOME_MSG, color='green')
    cred = get_credentials()
    vms = get_vms(cred)

    while True:
        selection = get_operation()

        if selection['operation'] == 'list':
            vms = get_vms(cred)
            print_vms(vms)
        elif selection['operation'] == 'power':
            vm_power = select_vm(vms)
            change_power_state(cred, vm_power['uuid'])
        elif selection['operation'] == 'delete':
            vm_delete = select_vm_delete(vms)
            if vm_delete['confirm']:
                delete_vm(cred, vm_delete['uuid'])
        elif selection['operation'] == 'clone':
            vm_clone = select_vm_clone(vms)
            clone_vm(cred, vm_clone['uuid'], int(vm_clone['count']))
        elif selection['operation'] == 'exit':
            exit(0)


if __name__ == '__main__':
    main()
