#!/usr/bin/env python3

import sys
from config import load_config
from dhcp import dhcp_list
from validation import valid_ip

def show_help():
    """
    Affiche un message d'aide expliquant comment utiliser la commande si l'option -h ou --help est utilisée
    """
    
    print('This command without any arguments will list the configuration files for each DHCP server defined in the YAML file')
    print('Usage: list-dhcp.py [DHCP IP address]')
    print('Example 1 : list-dhcp.py')
    print('Example 2 : list-dhcp.py 10.20.2.5')
    return

def list_dhcp(serv_dhcp=None):
    """ 
    
    Liste les clients DHCP (associations MAC/IP) enregistrés pour un ou plusieurs serveurs.

    Paramètre :
    - serv_dhcp : adresse IP d’un serveur DHCP spécifique à interroger. 
                  Si None, la commande s’applique à tous les serveurs listés dans le fichier YAML.
                  
    """


    #Charge le fichier de config YAML
    cfg = load_config('file.yaml', False)

    #Si le fichier n'existe pas et qu'on a demandé à ne pas le créer automatiquement
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

    #Cas où une IP de serveur DHCP a été spécifiée en argument
    if serv_dhcp != None:
        
        if valid_ip(serv_dhcp) == False:
            print('Error IP address',file=sys.stderr)
            show_help()
            return
        
        trouve=False
        
        #On vérifie que l’adresse IP est bien présente dans la config
        for serv in cfg.get('dhcp-servers'):
            if serv_dhcp == serv:
                serv_dhcp = serv #On garde la valeur exacte trouvée
                trouve=True
                break

        #Si on a pas pu identifier de serveur DHCP
        if trouve == False:
            print('cannot identify DHCP server',file=sys.stderr)
            return


        #Récupération et affichage des couples MAC/IP pour le serveur DHCP trouvé
        liste = dhcp_list(serv_dhcp,cfg)
        for elem in liste:
            mac = elem.get('mac')
            ip = elem.get('ip')           
            print(f"{mac:30} {ip}")


    #Cas où aucun serveur spécifique n’a été demandé : on liste tous les serveurs
    if serv_dhcp == None:
        for serv in cfg.get('dhcp-servers'):
            print(f"{serv}:")
            liste = dhcp_list(serv,cfg)
            for elem in liste:
                mac=elem.get('mac')
                ip = elem.get('ip')
                print(f"{mac:30} {ip}")
        
        
def main():
    """ 
    Fonction principale
    """

    #Affichage de l'aide si -h ou --help est passé en argument
    if len(sys.argv) == 2 and sys.argv[1] in ['-h','--help']:
        show_help()
        return

    #Aucun argument : on liste tous les serveurs DHCP
    if len(sys.argv) == 1:

        list_dhcp() 

    #Un argument : on liste la configuration du serveur passé en argument
    elif len(sys.argv) == 2:    
        ip = sys.argv[1]          
        list_dhcp(ip)

    #Plus d'un argument : erreur de syntaxe
    else:

        print('Syntax error')
        show_help()
        return
    
if __name__ == '__main__':
    main()
