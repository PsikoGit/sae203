#!/usr/bin/env python3

import sys
from fabric import Connection
from validation import valid_ip,valid_mac
from config import load_config,get_dhcp_server
from dhcp import dhcp_add
from paramiko.ssh_exception import NoValidConnectionsError
from invoke.exceptions import UnexpectedExit

def show_help():
    """
    Affiche un message d'aide expliquant comment utiliser la commande si l'option -h ou --help est utilisée
    """
    
    print('The command allows you to add a MAC/IP association to the DHCP server on the same network as the specified IP')
    print("Usage: add-dhcp-client.py MAC IP")
    print("Example: add-dhcp-client.py aa:bb:cc:dd:ee:ff 10.20.1.100")
    print('Allowed options : [-show] [-h] [--help]')
    return

def show_dhcp():
    """ 
    Affiche les serveurs DHCP qui sont configures dans le fichier YAML
    """

    cfg = load_config('file.yaml',True)

    if cfg == None:
        print("The configuration file doesn't exist and parameter create = False",file=sys.stderr)
        print("Manually create the YAML configuration file by following the documentation.",file=sys.stderr)
        return  

    #Si une erreur est survenue lors du chargement du fichier
    if cfg == False:
        print("Error while attempting load yaml file configuration",file=sys.stderr)
        return

    #Si la clé 'dhcp-servers' est absente du fichier de configuration
    if cfg.get('dhcp-servers') == None:
        print('No DHCP servers found in YAML configuration file, dhcp-servers keys are missing',file=sys.stderr)
        print('Append DHCP ip address on YAML configuration file by following the official documentation',file=sys.stderr)
        return

    for serv_dhcp in cfg.get('dhcp-servers'):
        print(f'DHCP server defined in the YAML file : {serv_dhcp}')


def add_dhcp_client(mac,ip):
    """ 
    Ajoute une association MAC/IP au serveur DHCP approprié
    """
    
    #Validation de l'adresse MAC
    if valid_mac(mac) == False:  
        print('error: bad MAC address',file=sys.stderr)  
        return
    
    #Validation de l'adresse IP
    if valid_ip(ip) == False:
        print('error: bad IP address',file=sys.stderr)  
        return

    cfg = load_config('file.yaml',False)

    #Si le fichier n'existe pas et qu'on a demandé à ne pas le créer automatiquement
    if cfg == None:
        print("The configuration file doesn't exist and parameter create = False",file=sys.stderr)
        print("Manually create the YAML configuration file by following the documentation",file=sys.stderr)
        return

    #Si une erreur est survenue lors du chargement du fichier
    if cfg == False:
        print("Error while attempting load yaml file configuration",file=sys.stderr)        
        return 

    #Si la clé 'dhcp-servers' est absente du fichier de configuration
    if cfg.get('dhcp-servers') == None:
        print('No DHCP servers found in YAML configuration file, dhcp-servers keys are missing',file=sys.stderr)
        print('Append DHCP IP address on YAML configuration file by following the official documentation',file=sys.stderr)
        return

    user = cfg.get('user')
    
    #Identification du serveur DHCP approprié
    serv_dhcp = get_dhcp_server(ip,cfg)
    
    if serv_dhcp == None:
        print('Unable to identify DHCP server',file=sys.stderr)
        return 

    serv_dhcp = list(serv_dhcp.keys())[0] #Pour contrer le dict_keys(['X.X.X.X'])

    #Vérifie que l'IP demandée n'est pas celle du serveur DHCP
    if str(ip) == serv_dhcp:
        print("Error: That's the DHCP IP address, retry",file=sys.stderr)
        return

    cnx = Connection(host=serv_dhcp, user=user, connect_kwargs={"key_filename": f"/home/{user}/.ssh/id_rsa"})

    try:
        #Ajout de l'association DHCP
        result = dhcp_add(ip,mac,serv_dhcp,cfg)

    except NoValidConnectionsError:
        print(f"SSH connection error with {serv_dhcp} server",file=sys.stderr)
        return

    if result == 3: #S'il y'a eu une modification sur le serveur distant

        try:
            cnx.run('sudo systemctl restart dnsmasq')
        except NoValidConnectionsError:
            print(f"SSH connection failed with {serv_dhcp} server",file=sys.stderr)
        except UnexpectedExit:
            print(f"systemctl restart dnsmasq command failed on {serv_dhcp}",file=sys.stderr)
        
        return

    if result == 2: #Si l'IP est déjà utilisée par cet hôte

        print('IP already used by this host',file=sys.stderr)
        return

    if result == 1: #Si l'IP est déjà utilisée par une autre machine
        print('IP already used by another device',file=sys.stderr)
        return       
    
        
def main():
    """ 
    Programme principal
    """

    if len(sys.argv) == 2 and sys.argv[1] == '-show':
        show_dhcp()
        return
    
    #Affiche l'aide si argument -h ou --help
    if len(sys.argv) == 2 and sys.argv[1] in ['-h','--help']:
        show_help()
        return
    
    if len(sys.argv) != 3:
        print("Syntax error")
        show_help()
        return

    mac = sys.argv[1]
    ip = sys.argv[2]
    
    add_dhcp_client(mac,ip)
    
    
if __name__ == '__main__':
    main()
