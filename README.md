<h2>Pré-requis techniques :</h2>

Avoir un environnement avec des machines Linux qui supportent python3, pip3 et fabric.

Avoir un utilisateur commun sur toutes les machines (serveur central et serveurs DHCP)

Disclaimer : Il faut avoir fini toute la procédure d'installation (que ça soit création du groupe sur les serveurs DHCP, etc...) pour que les codes soient fonctionnels.

<h2>Présentation des fichiers</h2>

<code>file.yaml</code> : fichier YAML de configuration utilisé pour les scripts python

<code>install.sh</code> : script qui installe et automatise certaines choses : installations des paquets et dépendances nécessaires, gestion des droits d'exécutions, permettre d'exécuter les scripts python depuis n'importe quel répertoire et création du fichier YAML de manière dynamique <br>

<code>configure_yaml.py</code>, <code>install_dependencies.sh</code> : sont des scripts appelés dans le fichier <code>install.sh</code> <br>

<code>code_dhcp/ssh-limiter.py</code> : code python qui permet de faire un filtrage ssh et laisse passer seulement les commandes présente dans les scripts python <br>

<code>README.md</code> : est le fichier que vous lisez actuellement, il contient les instructions concernant la présentation et l'installation de ma solution, et un guide d'utilisation des commandes Python. <br>

<code>dhcp.py</code>, <code>config.py</code>, <code>validation.py</code> : sont des scripts python nécessaire au fonctionnement des commandes principales, à savoir :

<code>add-dhcp-client.py</code> : permet d'ajouter une assocation MAC/IP dans la configuration dnsmasq des serveurs DHCP <br>

<code>remove-dhcp-client.py</code> : permet de retirer une association MAC/IP dans la configuration dsnmasq des serveurs DHCP <br>

<code>check-dhcp.py</code> : permet de vérifier la cohérence des fichiers de configuration dsnmasq des serveurs DHCP, voir s'il y'a des doublons d'adresse IP par exemple <br>

<code>list-dhcp.py</code> : permet un affichage formatté de la configuration dnsmasq des serveurs DHCP <br>

<h2>Syntaxe et utilisation des commandes </h2>

Pour toute les commandes (<code>add-dhcp-client.py</code>,<code>remove-dhcp-client.py</code>,<code>check-dhcp.py</code>,<code>list-dhcp.py</code>) il y'a des options en communs qui sont : <br>

<code>-show</code> : permet de voir les serveurs DHCP configurés dans le fichier yaml, exemple de sortie : 

<pre>
sae203@srv-central:~$ add-dhcp-client.py -show
DHCP server defined in the YAML file : 10.20.1.5
DHCP server defined in the YAML file : 10.20.2.5
</pre>

<code>-h</code> ou <code>--help</code> : permet d'afficher une brève explication de ce que fait la commande appelée et la syntaxe d'utilisation de celle-ci, exemple : 

<pre>
sae203@srv-central:~$ add-dhcp-client.py -h
The command allows you to add a MAC/IP association to the DHCP server on the same network as the specified IP
Usage: add-dhcp-client.py MAC IP
Example: add-dhcp-client.py aa:bb:cc:dd:ee:ff 10.20.1.100
Allowed options : [-show] [-h] [--help]
</pre>

<h2>Instructions serveur-central :</h2>

Pour choisir votre serveur central, il faudra qu'il soit capable de communiquer avec tous les réseaux sur lequel se trouve un serveur DHCP que vous voulez superviser. Un exemple de topologie peut-être un serveur central relié à 2 VLANs sur lesquels se trouvent respectivement un serveur DHCP (voir schéma ci-dessous)
   
                                                         [ Machine Centrale ]
                                                           /              \
                                                          /                \
                                                  [ Réseau 1 ]          [ Réseau 2 ]
                                                     |                       |
                                             [ Serveur DHCP 1 ]      [ Serveur DHCP 2 ]

Il n'y a pas de restrictions quant au nombre de réseaux/serv_dhcp supervisés, chaque serveur dhcp et réseau doivent être configurés dans le fichier YAML qui se trouve dans le repo github, les scripts python se basent sur ce fichier YAML pour fonctionner.

Sur le serveur central, une fois que vous avez importés le dossier github, il faudra exécuter le script install.sh via la commande <code>./install.sh</code> , si le script install.sh n'est pas exécutable rendez le exécutable via la commande <code>chmod +x install.sh</code> et relancer le script.

Ce script va vous permettre de rendre exécutable tous les fichiers qui doivent l'être, d'installer les dépendances et les paquets nécessaires au fonctionnement des scripts, de faire en sorte de pouvoir exécuter les commandes python de supervision DHCP depuis n'importe quel dossier de votre terminal et de créer le fichier YAML de manière dynamique. Suivez bien les instructions au niveau du ficher YAML.

Une fois que c'est fait, il faut créer un groupe, vous pouvez le nommer comme vous voulez, dans mon exemple je vais le nommer <code>superv</code>, il faut donc faire la commande <code>sudo groupadd superv</code>, et pour attribuer un utilisateur au groupe qui sera utilisé sur tous vos serveurs (celui spécifié dans le fichier YAML), dans mon exemple, le même utilisateur que je vais utilisé sur chaque serveur se nomme <code>sae203</code>, je vais donc exécuter la commande : <code>sudo usermod -aG superv sae203</code>
Ça va nous servir pour pouvoir faire certaines commandes qui nécessitent les droits sudo sans pour autant avoir besoin de renseigner le mot de passe.

Il vous faudra une paire de clé rsa ssh privée/publique sans mot de passe, pour se faire, sur le serveur central, entrer la commande : <code>ssh-keygen -t rsa</code>, ⚠️IMPORTANT⚠️ : laissez le nom par défaut des fichiers qui contiennent les clés (id_rsa et id_rsa.pub) sinon les codes ne vont pas fonctionner.
Transférez ensuite votre clé publique sur le/les serveur(s) DHCP distant(s), vous pouvez utiliser scp, exemple : <code>scp ~/.ssh/id_rsa.pub user@ip_dhcp:</code>, il faudra avoir installé au préalable le paquet ssh sur le/les serveur(s) DHCP, ensuite aller sur le serveur DHCP et faire <code>cat ~/id_rsa.pub >> ~/.ssh/authorized_keys</code>, désormais, il vous sera possible de vous connecter au serveur DHCP distant via ssh sans mot de passe, répétez la même procédure pour tout vos serveurs DHCP.

<h2>Instructions serveur DHCP :</h2>

Le service DHCP devra être fourni via le paquet <code>dnsmasq</code> qui devra être installée sur votre serveur, le fichier de configuration contenant les assocations entre MAC et IP devra se trouver dans le répertoire <code>/etc/dnsmasq.d/</code>, le nom du fichier doit respecter le format suivant : uniquement des lettres (a-z, A-Z), des tirets (<code>-</code>) et des underscores (<code>_</code>)

Il faut <b>obligatoirement</b> que la première ligne du fichier de configuration dhcp soit un commentaire.

Sur le serveur DHCP, il faudra effectuer un filtra ssh et un filtrage sudo.

Filtrage sudo :

Il faudra créer un groupe sur votre serveur DHCP avec la commande <code>sudo groupadd [GROUP]</code>, il faudra que le groupe porte le même nom que le groupe créé sur le serveur central, pour attribuer un utilisateur au groupe on fait <code>sudo usermod -aG [GROUP] [USER]</code> et modifier le fichier <code>/etc/sudoers</code> via la commande <code>sudo visudo</code> pour rajouter la ligne suivante : <code>%[GROUP] ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart dnsmasq , /usr/bin/sed * [chemin/vers/fichier/dnsmasq]</code>, ça va permettre d'autoriser les membres du groupe [GROUP] à exécuter les commandes <code>systemctl restart dnsmasq</code> et les commandes qui commencent par sudo sed et finissent par <code>/etc/dnsmasq.d/[...]</code> avec les droits sudo sans mot de passe, ça permet d'éviter de rentrer le mot de passe sudo de la machine distante à chaque fois qu'on veut exécuter les commandes python.

Filtrage ssh :

Il faudra récupérer le script qui se trouve dans le répertoire <code>code_dhcp</code> sur le dépot GitHub et le mettre sur votre serveur DHCP, dans mon exemple le script se trouve à <code>~/bin/ssh-limiter.py</code>, rendez le script exécutable si nécessaire. Vous 

Cette étape consiste à modifier le fichier <code>~/.ssh/authorized_keys</code>, actuellement votre fichier contient la clé publique de votre serveur central qui commence par <code>ssh-rsa AAAAB3NzaC1yc2E...</code>, il faudra rajouter cette chaîne de caractère juste avant la clé publique : <code>command="/chemin/vers/ssh-limiter.py",no-port-forwarding,no-X11-forwarding,no-agent-forwarding</code>, pour que ça donne à la fin :
<pre>
command="/home/sae203/bin/ssh-limiter.py",no-port-forwarding,no-X11-forwarding,no-agent-forwarding ssh-rsa AAAAB3NzaC1yc2EAAA...
</pre>

Ça permet de laisser passer seulement via SSH les commandes qui se trouvent dans les scripts Python, les autres commandes seront bloqués automatiquement.

<h2>FICHIER YAML :</h2>

Le fichier doit s'appeler obligatoire file.yaml et se trouver dans le <b>même</b> répertoire que les scripts python, il se constitue de cette sorte :
<pre>
dhcp_hosts_cfg:
user:
dhcp-servers:
</pre>

À la clé dhcp_hosts_cfg il faudra renseigner le chemin absolu du fichier dnsmasq de vos serveurs DHCP distant. <br>
À la clé user il faudra renseigner le nom d'utilisateur en commun sur tous vos serveurs <br>
À la clé dhcp-servers il faudra renseigner un/des dictionnaire(s) avec l'adresse IP du serveur DHCP en tant que clé et le réseau dans lequel il se situe en tant que valeur, voici un exemple : 
<pre>
dhcp_hosts_cfg: /etc/dnsmasq.d/hosts.conf
user: sae203
dhcp-servers:
   10.20.1.5: 10.20.1.0/24
   10.20.2.5: 10.20.2.0/24
</pre>



