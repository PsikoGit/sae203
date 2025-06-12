#!/bin/bash

#Etape 0 : Rendre tous les scripts executables (si y'a un bug et que ce n'est pas fait)

chmod +x remove-dhcp-client.py list-dhcp.py install_dependencies.sh configure_yaml.py check-dhcp.py add-dhcp-client.py


#Etape 1 : installer les modules python fabric et pyyaml via pip3 

./install_dependencies.sh

#Etape 2 : Ajouter le PATH s'il n'y est pas

CURRENT_DIR=$(pwd)

if ! grep -q "$CURRENT_DIR" ~/.bashrc; then

    echo "export PATH=\"\$PATH:$CURRENT_DIR\"" >> ~/.bashrc

    echo "Ajout de $CURRENT_DIR au PATH dans .bashrc"
else
    echo "Le PATH est deja present dans .bashrc"
fi

source ~/.bashrc

#Etape 3 : Creer le fichier YAML

echo ""
python3 configure_yaml.py
