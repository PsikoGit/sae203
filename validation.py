import ipaddress
import re

def valid_network(network):
    """
    Vérifie si l'adresse passée en paramètre est une adresse de réseau valide.
    Exemple : 10.20.1.0/24 retournera True et 10.20.1.5/24 retournera False car ce n'est pas
    une adresse de réseau.
    """

    try:
        ipaddress.IPv4Network(network,strict=True) #Accepte que les adresses de réseau strictement
        return True
    except ValueError:
        return False
        
def valid_ip(ip):
    """
    Vérifie que l'adresse IP reçue en paramètre est un adresse IPv4 valide.
    """
    
    try:
        #Vérification que l'IP peut être convertie en objet IPv4Address
        ipaddress.IPv4Address(ip)       
    except ipaddress.AddressValueError:
        #Si l'IP n'est pas valide, retourner False
        return False
    
    #Création de l'objet IP pour les vérifications suivantes
    ip = ipaddress.IPv4Address(ip)
        
    #Vérification que l'IP n'est pas dans les catégories d'adresses non utilisables    
    if (ip.is_loopback == True or      #Adresses de bouclage (127.x.x.x)
        ip.is_link_local == True or    #Adresses link-local (169.254.x.x)
        ip.is_multicast == True or     #Adresses multicast (224.x.x.x - 239.x.x.x)
        ip.is_unspecified == True or   #Adresse non spécifiée (0.0.0.0)
        ip.is_reserved == True):       #Adresses réservées
            
        return False
    
    return True
        
    
def valid_mac(mac):    
    """
    Vérifie que l'adresse MAC reçu en paramètre est valide    
    """
    
    #Vérification que ce n'est pas une adresse MAC nulle (non utilisable)
    if mac == '00:00:00:00:00:00':
        return False
    
    #Vérification que l'adresse MAC contient exactement 6 octets séparés par ':'
    if len(mac.split(':')) != 6:
        return False
    
    #Vérification que chaque octet est composé de 2 caractères hexadécimaux
    for cara in mac.split(':'):
        if not re.fullmatch('[0-9a-fA-F]{2}', cara):
            return False
    return True

def main():
    """Fonction principale pour tester les fonctions de validation."""
    
    #Données de test
    ip = '192.165.0.1'
    mac = 'AA:AA:AA:AA:AA:AA'
    
    #Tests de validation
    print(valid_ip(ip))
    print(valid_mac(mac))
    
    
    #Test d'une IP valide
    assert valid_ip('10.0.0.1') == True
    
    #Test d'une IP invalide
    assert valid_ip('256.256.256.256') == False   
    assert valid_ip('toto') == False
    
    #Test d'une IP de bouclage
    assert valid_ip('127.0.0.1') == False
    
    #Test d'une MAC valide
    assert valid_mac('03:1A:22:FF:EE:E2') == True
    
    #Test d'une MAC invalide (trop courte)
    assert valid_mac('AA:BB:CC') == False
    
    #Test de la MAC nulle  
    assert valid_mac('00:00:00:00:00:00') == False 

if __name__ == '__main__':
    main()
