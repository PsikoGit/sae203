#!/bin/bash

#Etape 1 : installer les modules python fabric et pyyaml via pip3 

chmod +x install_dependencies.sh
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
echo "CONFIGURATION DU FICHIER YAML"
echo ""
python3 configure_yaml.py
