#!/usr/bin/env python3

import sys
from config import load_config
from dhcp import check_dhcp_list
from validation import valid_ip,valid_network
from paramiko.ssh_exception import NoValidConnectionsError
from pathlib import Path

def show_help():
    """
    Affiche un message d'aide expliquant comment utiliser la commande si l'option -h ou --help est utilisée
    """
    
    print('This command without any arguments checks the configurations of all DHCP servers in the YAML file to detect the duplicates')
    print('Usage: check-dhcp.py [DHCP IP address or DHCP Network address]')
    print('Example 1 : check-dhcp.py')
    print('Example 2 : check-dhcp.py 10.20.1.5')
    print('Allowed options : [-show] [-h] [--help]')
    return

def show_dhcp():
    """ 
    Affiche les serveurs DHCP qui sont configures dans le fichier YAML
    """
    script_dir = Path(__file__).parent
    file = script_dir / 'file.yaml'
    file_abs = file.resolve()
    
    cfg = load_config(file_abs,False)

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


def check_dhcp(serv_dhcp=None):
    """
    Vérifie les configurations DHCP pour un serveur donné ou pour tous les serveurs listés
    dans le fichier YAML, en détectant les erreurs d'attribution.

    Paramètre :
    - serv_dhcp : adresse IP du serveur DHCP ou réseau DHCP à vérifier.
                  Si None, on vérifie tous les serveurs de la config YAML.
    """

    script_dir = Path(__file__).parent
    file = script_dir / 'file.yaml'
    file_abs = file.resolve()
    
    #Chargement du fichier de configuration YAML
    cfg = load_config(file_abs, False)


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
        print('Append DHCP ip address on YAML configuration file by following the official documentation',file=sys.stderr)
        return
      
    #Si un serveur spécifique est demandé
    if serv_dhcp != None:
        
        if valid_ip(serv_dhcp) == False and valid_network(serv_dhcp) == False:
            print('Error IP address',file=sys.stderr)
            show_help()
            return
        
        trouve=False
        
        #Parcours des serveurs DHCP et de leurs réseaux dans la config YAML (dictionnaire)
        for serv,net in cfg.get('dhcp-servers').items():
            #On accepte une correspondance soit sur l'IP serveur soit sur le réseau
            if serv_dhcp == serv or serv_dhcp == net:
                serv_dhcp = serv # Conserver la clé exacte du serveur trouvé
                trouve=True
                break

        #Si on a rien trouvé
        if trouve == False:
            print('cannot identify DHCP server',file=sys.stderr)
            return

        #On appel la fonction qui vérifie la config pour un serveur DHCP
        try:
            check_dhcp_list(serv_dhcp,cfg)
        except NoValidConnectionsError:
            print(f"SSH connection error with {serv_dhcp} server",file=sys.stderr)
            return
            
            
    #Si aucun serveur n'est passé en argument, on vérifie tous les serveurs DHCP
    if serv_dhcp == None:
        
        for serv in cfg.get('dhcp-servers'):
            
            try:
                check_dhcp_list(serv,cfg)
            except NoValidConnectionsError:
                print(f"SSH connection error with {serv} server",file=sys.stderr)
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

    #Aucun argument : vérifie tous les serveurs
    if len(sys.argv) == 1:
        check_dhcp() 

    #Un argument : vérifie le serveur/réseau passé en paramètre
    elif len(sys.argv) == 2:

        check_dhcp(sys.argv[1])

    #Plus d'un argument : erreur de syntaxe
    else:
        print('Syntax error')
        show_help()
        return
    
if __name__ == '__main__':
    main()
