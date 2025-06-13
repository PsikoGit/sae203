import ipaddress
import yaml
import os
import sys
from pathlib import Path

def load_config(filename, create):
    """
    Charge un fichier de configuration YAML ou le crée s'il n'existe pas.
    """
    script_dir = Path(__file__).parent
    filename = script_dir / 'file.yaml'
    filename = filename.resolve()
    #Vérification si le fichier existe et est bien un fichier
    if os.path.exists(filename) and os.path.isfile(filename):
        
        try:
            #Ouverture et lecture du fichier YAML existant
            with open(filename,'r') as fd:
                
                config = yaml.safe_load(fd)
                
        except yaml.YAMLError: #Gestion des erreurs de format YAML
            
            return False
        
    else: #Si le fichier n'existe pas       
        
        if create == True:
            
            #Création d'un dictionnaire de configuration par défaut
            dic = {'dhcp_hosts_cfg': '/etc/dnsmasq.d/hosts.conf', 'user': 'sae203'}
            
            #Création du fichier avec la configuration par défaut
            with open(filename,'w') as fd:
                
                yaml.dump(dic,fd,sort_keys=False) #Écrit dans le fichier

            try:
                with open(filename,'r') as fd:
                
                    config = yaml.safe_load(fd) #Charge dans une variable config en format python
            except yaml.YAMLError:
                return False
                
        else: #Si create=False et le fichier n'existe pas
            
            return None        
        
    return config

def get_dhcp_server(ip,cfg):   
    """
    Trouve le serveur DHCP correspondant à une adresse IP donnée.
    """
    
    #Conversion de l'IP en objet IPv4Address
    ip = ipaddress.IPv4Address(ip)
    

    if cfg.get('dhcp-servers') == None:
        return None
    
    #Parcours des serveurs DHCP et de leurs réseaux
    for ip_dhcp,network in cfg.get("dhcp-servers").items():
        
        # Vérification si l'IP appartient au réseau du serveur DHCP
        if ip in ipaddress.IPv4Network(network):
            
            return {ip_dhcp:network}
    
    #Aucun serveur DHCP trouvé pour cette IP
    return None

def main():
    """Fonction principale pour tester les fonctions de configuration."""
    
    #Données de test
    ip = '10.20.2.150'   
    filename = 'file.yaml'
    
    #Test de chargement de configuration
    cfg = load_config(filename,True)

    if cfg == False:
        print('Error while attempting load yaml file configuration',file=sys.stderr)
        return

    if cfg == None:
        print("The configuration file doesn't exist and parameter create = False",file=sys.stderr)
        return
        
    #Test de recherche de serveur DHCP
    print(get_dhcp_server(ip,cfg))
    
    #Assertions pour vérifier le bon fonctionnement
    #Test avec un fichier inexistant et create=False
    
    assert load_config('inexistant.yaml', False) is None
    
    #Test avec une IP valide (nécessite une configuration appropriée)
    #config_test = load_config(filename, True)
    assert load_config(filename,True) is not None 

    assert get_dhcp_server('0.0.0.0',cfg) == None    
    
if __name__ == '__main__':
    main()
