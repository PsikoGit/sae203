#!/usr/bin/env python3

import yaml
import os

# Chargement du fichier existant
yaml_file = "file.yaml"

# Vérifie que le fichier existe
if not os.path.exists(yaml_file):
    print(f"Erreur : le fichier {yaml_file} n'existe pas.")
    exit(1)

with open(yaml_file, 'r') as f:
    data = yaml.safe_load(f)

if data is None:
    data = {}

# Demande interactive

# 1. Chemin fichier DHCP
dhcp_path = input("Chemin absolu du fichier de configuration DHCP (ex: /etc/dnsmasq.d/hosts.conf) : ").strip()

while not dhcp_path.startswith('/etc/dnsmasq.d/'):
    dhcp_path = input("Le fichier de configuration dnsmasq doit se trouver dans le repertoire /etc/dnsmasq.d uniquement : ").strip()
    
data['dhcp_hosts_cfg'] = dhcp_path

# 2. User SSH
user = input("Nom d'utilisateur SSH (ex: sae203) : ").strip()
data['user'] = user

# 3. Serveurs DHCP
data['dhcp-servers'] = {}

print("\nAjout des serveurs DHCP (laisser vide pour terminer)")

i = 1
while True:

    if i == 1:
        print('Attention, ce script ne vérifie pas la cohérence des adresses IP que vous entrez, soyez vigilants\n')

    server_ip = input(f"Adresse IP du serveur DHCP {i} (ex: 10.20.1.5) : ").strip()
    if not server_ip:
        break
    if server_ip:
        i += 1
    subnet = input(f"Reseau associe pour {server_ip} (ex: 10.20.1.0/24) : ").strip()
    data['dhcp-servers'][server_ip] = subnet

#Sauvegarde
with open(yaml_file, 'w') as f:
    yaml.dump(data, f, default_flow_style=False,sort_keys=False)

print(f"\nFichier {yaml_file} mis à jour avec succès.")
