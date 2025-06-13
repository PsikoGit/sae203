Pré-requis techniques :

Avoir un environnement avec des machines Linux qui supportent python3, pip3 et fabric.

Avoir un utilisateur commun sur toutes les machines (serveur central et serveurs DHCP), vous pouvez ajouter un utilisateur via la commande sudo adduser [USER] et mettre les mêmes informations sur chaque serveur.

Instructions serveur-central : 

Pour choisir votre serveur central, il faudra qu'il soit capable de communiquer avec tous les réseaux sur lequel se trouve un serveur DHCP que vous voulez superviser. Un exemple de topologie peut-être un serveur central relié à 2 VLANs sur lesquels se trouvent respectivement un serveur DHCP (voir schéma ci-dessous)
   
                                                         [ Machine Centrale ]
                                                           /              \
                                                           /                \
                                                  [ Réseau 1 ]          [ Réseau 2 ]
                                                     |                       |
                                             [ Serveur DHCP 1 ]      [ Serveur DHCP 2 ]

Il n'y a pas de restrictions quant au nombre de réseaux/serv_dhcp supervisés, chaque serveur dhcp et réseau doivent être configurés dans le fichier YAML qui se trouve dans le repo github, les scripts python se basent sur ce fichier YAML pour fonctionner. Il faut que le fichier YAML s'appel obligatoirement : file.yaml

Sur le serveur central, une fois que vous avez importés le dossier github, il faudra exécuter le script install.sh via la commande ./install.sh , si le script install.sh n'est pas exécutable rendez le exécutable via la commande chmod +x install.sh et relancer le script.

Ce script va vous permettre de rendre exécutable tous les fichiers qui doivent l'être et de faire en sorte de pouvoir exécuter les commandes python de supervision DHCP depuis n'importe quel dossier de votre terminal et de créer le fichier YAML de manière dynamique. Suivez bien les instructions au niveau du ficher YAML

Une fois que c'est fait, il faut créer un groupe qui se nommera superv pour l'utilisateur qui sera utilisé sur tous vos serveurs (celui spécifié dans le fichier YAML), dans mon exemple, le même utilisateur que je vais utilisé sur chaque serveur se nomme sae203, et le groupe se nomme superv, je vais donc exécuter la commande : sudo usermod -aG superv sae203
Ça va nous servir pour pouvoir faire certaines commandes qui nécessitent les droits sudo sans pour autant avoir besoin de renseigner le mot de passe.

Il vous faudra une paire de clé rsa ssh privée/publique sans mot de passe, pour se faire, sur le serveur central, entrer la commande : ssh-keygen -t rsa, laissez le nom des fichiers qui contiennent les clés par défaut (id_rsa et id_rsa.pub), transférez votre clé publique sur le/les serveur(s) DHCP distant(s), vous pouvez utiliser scp, exemple : scp ~/.ssh/id_rsa.pub user@ip_dhcp: , il faudra avoir installé au préalable le paquet ssh sur le/les serveur(s) DHCP, ensuite aller sur le serveur DHCP et faire cat ~/id_rsa.pub >> ~/.ssh/authorized_keys, désormais, il vous sera possible de vous connecter au serveur DHCP distant via ssh sans mot de passe, répétez la même procédure pour tout vos serveurs DHCP.

À la clé dhcp_hosts_cfg il faudra renseigner le chemin absolu du fichier dnsmasq de vos serveurs DHCP distant
