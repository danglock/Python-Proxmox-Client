from proxmoxer import ProxmoxAPI
import os # for clear or cls depending OS & list profiles
import json # to load config file
from termcolor import colored # to print in color
import time # Sleep time
import math # To convert Bytes in MB, GB, TB etc...
import argparse # for arguments


# Definition des attributs du parser
parser = argparse.ArgumentParser(
  description="My Parser Description")

# exemple d'argument -e / --encode
parser.add_argument("-p", "--profile", metavar="", required=False, help="Select a profile.")
# afin de récupérer le contenu du parser
args = parser.parse_args()





def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])




# Fonction Clear
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def create_profile():
    host = input("Host : ")
    username = input("Username (eg. user@pam) : ")
    tokenName = input("Token Name : ")
    tokenValue = input("Token Value : ")

    try :
        f = open(f"profiles/{args.profile}.json", "w")
        f.write("{\n    \"host\": "+"\""+host +"\","+"\n    \"username\": "+"\""+username+"\","+"\n    \"tokenName\": "+"\""+tokenName+"\","+"\n    \"tokenValue\": "+"\""+tokenValue+"\""+"\n}")
        f.close()
        print(colored("Profile created !", "green"))
        profile = f"profiles/{args.profile}.json"
    except :
        print(colored("Error during profile creation !", "red"))




# Chargement du profile

if args.profile :
    print(colored(f"Searching profile '{args.profile}'", "yellow"))

    # si le profile existe
    if os.path.exists(f"profiles/{args.profile}.json"):
        print(colored("Profile Selected", "green"))
        profile = f"profiles/{args.profile}.json"

    # if choosed profile doesn't exists
    else:
        # if profiles folder doesn't exists, create it
        if not os.path.exists("profiles/"):
            print("Creating profile folder...")
            os.makedirs("profiles/")
        
        print(colored(f"There is no profile named '{args.profile}'", "red"))
        print("Would you want to create a new one ?")
        x = input("[Y/n]: ")

        if x == "Y" or x == "y":
            host = input("Host : ")
            username = input("Username (eg. user@pam) : ")
            tokenName = input("Token Name : ")
            tokenValue = input("Token Value : ")

            try :
                f = open(f"profiles/{args.profile}.json", "w")
                f.write("{\n    \"host\": "+"\""+host +"\","+"\n    \"username\": "+"\""+username+"\","+"\n    \"tokenName\": "+"\""+tokenName+"\","+"\n    \"tokenValue\": "+"\""+tokenValue+"\""+"\n}")
                f.close()
                print(colored("Profile created !", "green"))
                profile = f"profiles/{args.profile}.json"
            except :
                print(colored("Error during profile creation !", "red"))
        else:
            # Listing existing profiles
            clear()
            print("Listing profiles...")
            proFiles = os.listdir("./profiles")
            proFiles.sort()
            proFilesCount = 0
            for file in proFiles :
                if file.endswith(".json"):
                    proFilesCount += 1
                    filename = file[:-5]
                    print(f"[{proFilesCount}] {filename}")
            
            x = int(input("Selection: "))
            profile = f"profiles/{proFiles[x - 1]}"
            print(f"Profile selected = {proFiles[x -1]}")


else:
    # Using default profile
    # If it doesn't exist, create it :
    if os.path.exists("profiles/default.json"):
        profile = "profiles/default.json"
    else :
        # if profile folder doesn't exists, create it
        if not os.path.exists("profiles/"):
            print("Creating profile folder...")
            os.makedirs("profiles/")

        print("Default profile doesn't exists. Creating it...")
        host = input("Host : ")
        username = input("Username (eg. user@pam) : ")
        tokenName = input("Token Name : ")
        tokenValue = input("Token Value : ")
        try :
            f = open(f"profiles/default.json", "w")
            f.write("{\n    \"host\": "+"\""+host +"\","+"\n    \"username\": "+"\""+username+"\","+"\n    \"tokenName\": "+"\""+tokenName+"\","+"\n    \"tokenValue\": "+"\""+tokenValue+"\""+"\n}")
            f.close()
            print(colored("Profile created !", "green"))
            profile = "profiles/default.json"
        except :
            print(colored("Error during profile creation !", "red"))




try:
    print(colored("Loading profile: ", "yellow") + f"{profile[9:-5]}")
    with open(profile) as configFile:
        settings = json.load(configFile)
    print("Configuration imported !")
except:
    print(colored("Error: ", "red") + "Unable to load profile configuration...")




# Connexion au serveur proxmox
try :
    print(colored("Connecting to the server...", "yellow"))
    proxmox = ProxmoxAPI( settings['host'], user=settings["username"], token_name=settings["tokenName"], token_value=settings["tokenValue"], verify_ssl=False ) #, verify_ssl=False # If SSL, then install and import "requests"
    proxmox.nodes.get() # Test connection
    print(colored(f"Connected to {settings['host']} !", "green"))
except :
    print(colored("Error: ", "red") + "Unable to connect to the Proxmox server. Please check your profile configuration and make sure you are able to contact the host.")
    exit()




nodes = []
vms = []
containers = []

for node in proxmox.nodes.get():
    nodes.append(node["node"])
    for virtman in proxmox.nodes.get(f"{node['node']}/qemu"):
        vms.append(virtman["vmid"])
    for cont in proxmox.nodes.get(f"{node['node']}/lxc"):
        containers.append(cont["vmid"])

nodes.sort()
vms.sort()
containers.sort()



print(f"Loaded :\n- {len(nodes)} Node(s)\n- {len(vms)} VMs\n- {len(containers)} Containers")
time.sleep(2)

def help():
    print(f"---{'-'*len(settings['host'])}---")
    print(f"|  {settings['host']}  |")
    print(f"---{'-'*len(settings['host'])}---\n")
    print(f"- {len(vms)} VMs\n- {len(containers)} Containers\n")
    print("[1] Virtual Machines")
    print("[2] Containers")

def NavHelp(inMenu = False):
    print("")
    if inMenu:
        print("[R] Return")
    print("[X] Exit")

def MachineHelp():
    print("")
    print("[1] Start        [3] Reboot         [5] Clone")
    print("[2] Shutdown     [4] Force Stop     [6] Edit ")

def EditHelp():
    print("-------------")
    print("|  Edition  |")
    print("-------------\n")
    print("[1] Rename")
    print("[D] Delete")

def coloreStatus(status):
    if status == "stopped":
        return colored("stopped", "red")
    elif status == "running":
        return colored("running", "green")
    else:
        return status



manual_launch = True

while manual_launch:
    clear()
    help()
    NavHelp()
    user_choice = input("\nCommand : ")


    if user_choice == "1":
        print("Loading VMs...")

        # Reload vms
        vms = []
        for node in proxmox.nodes.get():
            for virtman in proxmox.nodes.get(f"{node['node']}/qemu"):
                vms.append(virtman["vmid"])
        vms.sort()




        clear()
        print("-------------")
        print("|  VM List  |")
        print("-------------\n")
        count = 0
        for vm in vms:
            count += 1
            VMstats = proxmox.nodes.get(f"{node['node']}/qemu/{vm}/status/current")
            print(f"[{count}] {VMstats['vmid']}.{VMstats['name']} -> {coloreStatus(VMstats['status'])}")
        NavHelp(True)


        menu_vm = True
        while menu_vm:
            menu_choice = input("\nCommand : ")
            if menu_choice == "R" or menu_choice == "r":
                clear()
                help()
                menu_vm = False
            elif menu_choice == "X" or menu_choice == "x":
                exit()

            elif int(menu_choice) >= 1 and int(menu_choice) <= count:
                clear()
                VMid = vms[int(menu_choice) - 1]
                

                Menu1=True
                while Menu1:
                    clear()

                    VMstats = proxmox.nodes.get(f"{node['node']}/qemu/{VMid}/status/current")
                    VMconfig = proxmox.nodes.get(f"{node['node']}/qemu/{VMid}/config")

                    DiskSize = convert_size(VMstats['maxdisk'])
                    RamSize = convert_size(VMstats['maxmem'])

                    # Print VM stats

                    print(colored("Name   : ", "yellow"), VMstats['name'], f"\t--> {coloreStatus(VMstats['status'])}")
                    print(colored("Id     : ", "yellow"), VMstats['vmid'])
                    print(colored("CPUs   : ", "yellow"), VMstats['cpus'])
                    print(colored("Disk   : ", "yellow"), DiskSize)
                    print(colored("Memory : ", "yellow"), RamSize)

                    MachineHelp()
                    NavHelp(True)
                    VMmenu_choice = input("\nSelection : ")

                    if VMmenu_choice == "1":
                        start = proxmox.nodes.post(f"{node['node']}/qemu/{VMid}/status/start")
                        print(start)
                        time.sleep(2)
                    elif VMmenu_choice == "2":
                        shutdown = proxmox.nodes.post(f"{node['node']}/qemu/{VMid}/status/shutdown")
                        print(shutdown)
                        time.sleep(2)
                    elif VMmenu_choice == "3":
                        reboot = proxmox.nodes.post(f"{node['node']}/qemu/{VMid}/status/reboot")
                        print(reboot)
                    elif VMmenu_choice == "4":
                        stop = proxmox.nodes.post(f"{node['node']}/qemu/{VMid}/status/stop")
                        print(stop)
                        time.sleep(2)
                    elif VMmenu_choice == "X" or VMmenu_choice == "x":
                        exit()
                    elif VMmenu_choice == "R" or VMmenu_choice == "r":
                        clear()
                        help()
                        menu_vm = False
                        Menu1 = False
                    elif VMmenu_choice == "5":
                        try:
                            clear()
                            print(colored("Copy of : ", "yellow"), VMstats['name'])
                            id = input("\nProvide an id : ")
                            clone = proxmox.nodes.post(f"{node['node']}/qemu/{VMid}/clone?newid={id}")
                            print(clone)
                        except:
                            print(colored("An error occured :(", "red"))

                    elif VMmenu_choice == "6":

                        menu_edit = True
                        while menu_edit:
                            clear()
                            EditHelp()
                            NavHelp(True)
                            edit_choice = input("\nSelection : ")

                            if edit_choice == "D" or edit_choice == "d":
                                try:
                                    delete = proxmox.nodes.delete(f"{node['node']}/qemu/{VMid}")
                                    print(delete)
                                    menu_edit = False
                                except:
                                    print(colored("Error: ", "red"), "Unable to delete the VM")
                            elif edit_choice == "1":
                                print(f"Enter the new name for {VMstats['name']}")
                                name = input("Name : ")

                                rename = proxmox.nodes.post(f"{node['node']}/qemu/{VMid}/config?name={name}")

                                menu_edit = False
                            elif edit_choice == "x" or edit_choice == "x":
                                exit()
                            elif edit_choice == "R" or edit_choice == "r":
                                clear()
                                menu_edit = False








    elif user_choice == "2":
        print("Loading Containers...")


        # Reload Containers
        containers = []

        for node in proxmox.nodes.get():
            
            for cont in proxmox.nodes.get(f"{node['node']}/lxc"):
                containers.append(cont["vmid"])

        containers.sort()

        clear()
        print("--------------")
        print("| Containers |")
        print("--------------\n")

        count = 0
        for container in containers:
            count += 1
            ContainerStats = proxmox.nodes.get(f"{node['node']}/lxc/{container}/status/current")
            print(f"[{count}] {ContainerStats['vmid']}.{ContainerStats['name']} -> {coloreStatus(ContainerStats['status'])}")

        NavHelp(True)


        menu_vm = True
        while menu_vm:
            menu_choice = input("\nSelection : ")
            if menu_choice == "R" or menu_choice == "r":
                clear()
                help()
                menu_vm = False
            elif menu_choice == "X" or menu_choice == "x":
                exit()

            elif int(menu_choice) >= 1 and int(menu_choice) <= count:
                clear()
                VMid = containers[int(menu_choice) - 1]
                

                Menu1=True
                while Menu1:
                    clear()

                    VMstats = proxmox.nodes.get(f"{node['node']}/lxc/{VMid}/status/current")
                    VMconfig = proxmox.nodes.get(f"{node['node']}/lxc/{VMid}/config")

                    DiskSize = convert_size(VMstats['maxdisk'])
                    RamSize = convert_size(VMstats['maxmem'])

                    # Print VM stats

                    print(colored("Name  : ", "yellow"), VMstats['name'], f"\t--> {coloreStatus(VMstats['status'])}")
                    print(colored("Id    : ", "yellow"), VMstats['vmid'])
                    print(colored("CPUs  : ", "yellow"), VMstats['cpus'])
                    print(colored("Disk  : ", "yellow"), DiskSize)
                    print(colored("Memory: ", "yellow"), RamSize)

                    MachineHelp()
                    NavHelp(True)
                    VMmenu_choice = input("\nCommand : ")

                    if VMmenu_choice == "1": # Start
                        start = proxmox.nodes.post(f"{node['node']}/lxc/{VMid}/status/start")
                        print(start)
                        time.sleep(2) # Sleep to refresh status
                    elif VMmenu_choice == "2": # Shutdown
                        shutdown = proxmox.nodes.post(f"{node['node']}/lxc/{VMid}/status/shutdown")
                        print(shutdown)
                        time.sleep(2) # Sleep to refresh status
                    elif VMmenu_choice == "3": # Reboot
                        reboot = proxmox.nodes.post(f"{node['node']}/lxc/{VMid}/status/reboot")
                        print(reboot)
                    elif VMmenu_choice == "4": # Force Stop
                        stop = proxmox.nodes.post(f"{node['node']}/lxc/{VMid}/status/stop")
                        print(stop)
                        time.sleep(2) # Sleep to refresh status
                    elif VMmenu_choice == "X" or VMmenu_choice == "x":
                        exit()
                    elif VMmenu_choice == "R" or VMmenu_choice == "r":
                        clear()
                        help()
                        menu_vm = False
                        Menu1 = False
                    elif VMmenu_choice == "5":
                        try:
                            clear()
                            print(colored("Copy of : ", "yellow"), VMstats['name'])
                            id = input("\nProvide an id : ")
                            clone = proxmox.nodes.post(f"{node['node']}/lxc/{VMid}/clone?newid={id}")
                            print(clone)
                        except:
                            print(colored("An error occured :(", "red"))

                    elif VMmenu_choice == "6":

                        menu_edit = True
                        while menu_edit:
                            clear()
                            EditHelp()
                            NavHelp(True)
                            edit_choice = input("\nSelection : ")

                            if edit_choice == "D" or edit_choice == "d":
                                try:
                                    delete = proxmox.nodes.delete(f"{node['node']}/lxc/{VMid}")
                                    print(delete)
                                    menu_edit = False
                                except:
                                    print(colored("Error: ", "red"), "Unable to delete Container.")
                            elif edit_choice == "1":
                                print(f"Enter the new name for {VMstats['name']}")
                                name = input("Name : ")

                                rename = proxmox.nodes.post(f"{node['node']}/lxc/{VMid}/config?name={name}")

                                menu_edit = False
                            elif edit_choice == "x" or edit_choice == "x":
                                exit()
                            elif edit_choice == "R" or edit_choice == "r":
                                clear()
                                menu_edit = False
                    






    elif user_choice == "3":
        while True :
            for user in proxmox.nodes.get(f"/access/users/"):
                print(user)






    elif user_choice == "X" or user_choice == "x":
        exit()
    
        

# https://pve.proxmox.com/pve-docs/api-viewer/index.html
