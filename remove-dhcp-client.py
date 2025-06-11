#!/usr/bin/env python3

import sys
from fabric import Connection
from paramiko.ssh_exception import NoValidConnectionsError
from validation import valid_ip,valid_mac
from config import load_config
from dhcp import dhcp_remove
from invoke.exceptions import UnexpectedExit

def show_help():
    """
    Affiche un message d'aide expliquant comment utiliser la commande si l'option -h ou --help est utilisée
    """
    
    print('-This command allows you to remove a MAC/IP association based on the MAC address, without any arguments, that will remove the MAC/IP association from the first matching entry it finds\n')
    print('-With the -d option, you can specify the DHCP server on which you want to remove the MAC/IP assocation\n')
    print('Usage: remove-dhcp-client.py MAC or remove-dhcp-client.py -d MAC DHCP_IP_ADDRESS')
    print('Example 1 : remove-dhcp-client.py AA:AA:AA:AA:AA:AA')
    print('Example 2 : remove-dhcp-client.py -d BB:BB:BB:BB:BB:BB 10.20.1.5')
    print('Allowed options : [-d] [-show] [-h] [--help]')
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


def remove_dhcp_client_with_server(mac, serv_dhcp):
    """ 
    Supprime une association MAC/IP d'un serveur DHCP spécifique
    """

    #Validation de l'adresse MAC fournie
    if valid_mac(mac) == False:
        print('error: bad MAC address',file=sys.stderr)
        return

    #Validation de l'adresse IP fournie
    if valid_ip(serv_dhcp) == False:
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
    
    #Vérifie que le serveur DHCP spécifié existe dans la configuration
    trouve = False
    for ip in cfg.get('dhcp-servers'):

        if serv_dhcp == ip:
            trouve = True
            break
    #Si le serveur DHCP n'est pas trouvé dans la configuration
    if trouve == False:
        print('Unable to identify DHCP server in YAML configuration file',file=sys.stderr)
        return

    user = cfg.get('user')

    #Récupération du nom d'utilisateur depuis la configuration
    cnx = Connection(host=serv_dhcp, user=user, connect_kwargs={"key_filename": f"/home/{user}/.ssh/id_rsa"})
     
    #Établissement de la connexion SSH vers le serveur DHCP
    remove = dhcp_remove(mac,serv_dhcp,cfg)

    #Si il y'a eu une supression
    if remove == True:
        try:
            #Redémarre le service dnsmasq pour appliquer les changements
            cnx.run('sudo systemctl restart dnsmasq')
            return
        except NoValidConnectionsError:
            print(f"SSH connection error with {serv_dhcp} server",file=sys.stderr)   #on enlevera le return ici pour qu'il retourne dans la boucle et fasse son taff
            return
        except UnexpectedExit:
            print(f"systemctl restart dnsmasq command failed on {serv_dhcp}",file=sys.stderr)
            return
        
    #Si l'adresse MAC n'a pas été trouvée
    print('MAC address not found',file=sys.stderr)
    return

def remove_dhcp_client(mac):
    """
    Supprime une association MAC/IP en cherchant automatiquement sur tous les serveurs DHCP
    configurés jusqu'à trouver la première occurrence de l'adresse MAC
    """

    #Validation de l'adresse MAC fournie
    if valid_mac(mac) == False:
        print('error: bad MAC address',file=sys.stderr)
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
        print('Append DHCP Ip address on YAML configuration file by following the official documentation',file=sys.stderr)
        return
    
    #Récupération des paramètres de configuration
    file = cfg.get('dhcp_hosts_cfg')
    user = cfg.get('user')

    for serv_dhcp in cfg.get('dhcp-servers'):
        #Établissement de la connexion SSH vers chaque serveur
        cnx = Connection(host=serv_dhcp, user=user, connect_kwargs={"key_filename": f"/home/{user}/.ssh/id_rsa"})
        try:
            #Cherche l'adresse MAC dans le fichier de config
            grep = cnx.run(f'grep -i {mac} {file}',hide=True,warn=True)
            
        except NoValidConnectionsError:       
            print(f"SSH connection error with {serv_dhcp} server",file=sys.stderr)
            return
        
        #Si la commande s'est executee sans erreur (code 0) et que le texte retourne n'est pas vide
        if grep.ok and grep.stdout.strip(): 

            try:
                #Supprime l'adresse MAC trouvée dans le serveur correspondant
                remove = dhcp_remove(mac,serv_dhcp,cfg)

            except NoValidConnectionsError:
                print(f"SSH connection error with {serv_dhcp} server",file=sys.stderr)
                return
            
            #Si la suppression a réussi
            if remove == True:
                try:
                    #Redémarrage du service dnsmasq pour appliquer les changements
                    cnx.run('sudo systemctl restart dnsmasq')
                    return
                except NoValidConnectionsError:
                    print(f"SSH connection error with {serv_dhcp} server",file=sys.stderr)   #on enlevera le return ici pour qu'il retourne dans la boucle et fasse son taff
                    return
                except UnexpectedExit:
                    print(f"systemctl restart dnsmasq command failed on {serv_dhcp}",file=sys.stderr)
                    return
    #Si l'adresse MAC n'a été trouvée sur aucun serveur
    print('MAC address not found',file=sys.stderr)
    return

        
def main():
    """ 
    Fonction principale
    """

    if len(sys.argv) == 2 and sys.argv[1] == '-show':
        show_dhcp()
        return

    #Affiche l'aide si argument -h ou --help
    if len(sys.argv) == 2 and sys.argv[1] in ['-h','--help']:
        show_help()
        return    

    #Mode avec serveur spécifique : remove-dhcp-client.py -d MAC DHCP_IP
    if len(sys.argv) == 4 and sys.argv[1] == '-d':
        mac = sys.argv[2]               # Adresse MAC à supprimer
        serv_dhcp = sys.argv[3]         # Serveur DHCP cible
        remove_dhcp_client_with_server(mac,serv_dhcp)
        return

    # Mode automatique : remove-dhcp-client.py MAC
    # Recherche la MAC sur tous les serveurs 
    if len(sys.argv) == 2:
        mac = sys.argv[1]
        remove_dhcp_client(mac)
        return

    print('Syntax error')
    show_help()
    return    
    
if __name__ == '__main__':
    main()
