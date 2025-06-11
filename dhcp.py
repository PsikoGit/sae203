import ipaddress
import yaml
from fabric import Connection

def ip_other_mac_exists(cnx, ip, mac, cfg):
    """ 
    Vérifie si une IP est déjà utilisée par une autre adresse MAC.
    """
    #Conversion de l'IP en objet IPv4Address
    ip = ipaddress.IPv4Address(ip)
    
    #Récupération du chemin du fichier de configuration DHCP
    file = cfg.get('dhcp_hosts_cfg')

    #Lecture du contenu du fichier de configuration DHCP via SSH
    cat_file = cnx.run(f"cat {file}",hide=True) 
    
    result = cat_file.stdout.strip() #Transforme la sortie en string et supprime les espaces en trop

    #Chaque ligne deviens un élément d'une liste tout en ignorant la première ligne qui est un commentaire
    result = result.splitlines()[1:] 

    for line in result:
        parts = line.split(',')

        if len(parts) == 2:

            mac_in_file = parts[0].split('=')[1].lower()    #Extraction de l'adresse MAC
            ip_in_file = parts[1].strip()                   #Extraction de l'adresse IP

            #Si l'IP correspond avec une autre machine
            if ip_in_file == str(ip) and mac_in_file != mac.lower():

                return True 

    return False

def ip_and_mac_exists(cnx,ip,mac,cfg):
    """
    Vérifie si l'IP et la MAC sont déjà attribués ensemble dans le serveur DHCP distant.
    """
    
    ip = ipaddress.IPv4Address(ip)

    file = cfg.get('dhcp_hosts_cfg')

    #Lecture du contenu du fichier de configuration DHCP via SSH
    cat_file = cnx.run(f"cat {file}",hide=True)

    result = cat_file.stdout.strip()

    result = result.splitlines()[1:]

    for line in result:
        parts = line.split(',')

        if len(parts) == 2:

            mac_in_file = parts[0].split('=')[1].lower()    #Extraction de l'adresse MAC
            ip_in_file = parts[1].strip()                   #Extraction de l'adresse IP
            
            #Si l'IP correspond à la même adresse MAC
            if ip_in_file == str(ip) and mac_in_file == mac.lower():

                return True

    return False 
 
def mac_exists(cnx, mac, cfg):
    """
    Vérifie si l'adresse MAC existe dans la configuration DHCP.
    """
    
    file = cfg.get('dhcp_hosts_cfg')

    #Lecture du contenu du fichier de configuration DHCP via SSH
    cat_file = cnx.run(f"cat {file}",hide=True)
    
    result = cat_file.stdout.strip()

    result = result.splitlines()[1:]
    
    for line in result:

        parts = line.split(',')

        if len(parts) == 2:

            mac_in_file = parts[0].split('=')[1].lower() #Extraction de l'adresse MAC

            #Si l'adresse MAC se trouve dans le fichier
            if mac_in_file == mac.lower():
                return True

    return False

def mac_exists_line(cnx, mac, cfg):
    """
    Retourne le numéro de ligne où se trouve l'adresse MAC passée en paramètre. 
    """  
    
    file = cfg.get('dhcp_hosts_cfg')

    cat_file = cnx.run(f"cat {file}",hide=True) 

    result = cat_file.stdout.strip()

    result = result.splitlines()

    i = 0
    
    #Recupere la ligne a laquelle il a trouver la correspondance
    for line in result:

        i += 1

        parts = line.split(',')

        if len(parts) == 2:

            mac_in_file = parts[0].split('=')[1].lower()  #Extraction de l'adresse MAC

            if mac_in_file == mac.lower():

                return i #Numéro de la ligne correspondant


def dhcp_add(ip,mac,server,cfg):
    """
    Ajoute ou modifie une entrée DHCP avec l'IP et la MAC donnée.
    """
    
    ip = ipaddress.IPv4Address(ip)
    
    #Récupération des paramètres de configuration
    file = cfg.get('dhcp_hosts_cfg')
    user = cfg.get('user')
    
    #Établissement de la connexion SSH
    cnx = Connection(host=server, user=user, connect_kwargs={"key_filename": f"/home/{user}/.ssh/id_rsa"})

    if ip_other_mac_exists(cnx,ip,mac,cfg) == True:

        return 1 #return 1 = IP deja utilise par une autre adresse

    if ip_and_mac_exists(cnx,ip,mac,cfg) == True:
    
        return 2 #return 2 = IP deja configure pour cet hote

    if mac_exists(cnx,mac,cfg) == True:
 
        #Modification de la ligne existante avec sed
        cnx.run(f"sudo sed -i 's/^dhcp-host={mac}.*/dhcp-host={mac},{ip}/I' {file}")
        return 3 #return 3 = on a fait une modif

    else:

        #Ajout d'une nouvelle ligne à la fin du fichier via sed
        cnx.run(f"sudo sed -i '$ a dhcp-host={mac},{ip}' {file}")
        return 3


def dhcp_remove(mac,server,cfg):
    """
    Supprime une entrée DHCP basée sur l'adresse MAC.
    """

    #Récupération des paramètres de configuration
    file = cfg.get('dhcp_hosts_cfg')
    user = cfg.get('user')
    
    cnx = Connection(host=server, user=user, connect_kwargs={"key_filename": f"/home/{user}/.ssh/id_rsa"})

    #Si la MAC est présente dans le fichier de configuration DHCP 
    if mac_exists(cnx,mac,cfg):
        i = mac_exists_line(cnx,mac,cfg) #Récupère le numéro de la ligne à laquelle il trouve l'adresse MAC
        if i: #Verifie que c'est pas vide
            #Suppression de la ligne avec sed
            cnx.run(f"sudo sed -i '{i}d' {file}") #Pour contrer le probleme de la casse, on peut pas specifier d'option pour delete tout en ignorant la casse
            return True

    else:

        return False
    
def dhcp_list(server, cfg):
    """
    Liste toutes les entrées DHCP du serveur.
    """ 
    
    #Liste finale à retourner
    final_list = []

    file = cfg.get('dhcp_hosts_cfg')
    user = cfg.get('user')
    
    #Initialisation de la connexion SSH
    cnx = Connection(host=server, user=user, connect_kwargs={"key_filename": f"/home/{user}/.ssh/id_rsa"})

    cat_file = cnx.run(f'cat {file}',hide=True)

    result = cat_file.stdout.strip()

    result = result.splitlines()[1:]

    for line in result:

        parts = line.split(',')

        if len(parts) == 2:

            mac = parts[0].split('=')[1]  #Extraction de l'adresse MAC
            ip = parts[1].strip()         #Extraction de l'adresse IP
            
            
            #Affichage dans une liste de dictionnaires
            dic = {'mac':mac,'ip':ip}     
            final_list.append(dic)        

    return final_list


def check_dhcp_list(serv_dhcp,cfg):
    '''
    Verifie les occurences de MAC et IP localement au sein d'un serveur dhcp
    '''

    user = cfg.get('user')
    file = cfg.get('dhcp_hosts_cfg')
    
    cnx = Connection(host=serv_dhcp, user=user, connect_kwargs={"key_filename": f"/home/{user}/.ssh/id_rsa"})

    # Coupe les lignes en 2 colonnes en prenant comme separateur ',' puis selectionne la colonne de gauche
    # trie avec 'sort' en étant insensible à la casse
    # 'uniq -di' pour retourner ce qui est en doublon une seule fois et en etant insensible a la casse
    
   
    check_mac = cnx.run(f"cut -d ',' -f1 {file} | sort -f | uniq -di",hide=True)

    
    #Extraction des MACs dupliquées dans une liste
    mac_duplique = check_mac.stdout.strip().split()

    if mac_duplique: #Si la liste n'est pas vide, affichage des doublons de MAC
        print(f'duplicate MAC addresses in {serv_dhcp} cfg:')

        for add_mac in mac_duplique:           
            cnx.run(f'grep -i {add_mac} {file}')

        print() #Saut de ligne pour que ça soit plus lisible sur le terminal
    

    check_ip = cnx.run(f"cut -d ',' -f2 {file} | sort | uniq -d",hide=True)

    
    ip_duplique = check_ip.stdout.strip().split()
    
    if ip_duplique: #Si la liste n'est pas vide, affichage des doublons d'IP

        print(f'duplicate IP addresses in {serv_dhcp} cfg:')

        for add_ip in ip_duplique:           
           
            cnx.run(f"grep -w {add_ip} {file}")

        print()

        
def main():
    """Fonction principale pour tester les fonctions DHCP."""
    
    cnx = Connection(host='10.20.1.5', user='sae203', connect_kwargs={"key_filename": "/home/sae203/.ssh/id_rsa"})

    ip = '10.20.2.101'
    mac = 'EE:EE:EE:EE:EE:EE'
    
    with open('file.yaml','r') as fd:
 
        cfg = yaml.safe_load(fd)
        print(ip_other_mac_exists(cnx, ip, mac, cfg))
if __name__ == '__main__':
    main()
