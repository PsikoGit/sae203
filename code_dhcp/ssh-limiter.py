#!/usr/bin/env python3

import os
import sys
import subprocess

def is_command_allowed(cmd):
    """Verifie si une commande est autorisée - Liste stricte"""
    cmd = cmd.strip()
    
    # Liste exacte des commandes autorisées
    allowed_commands = [
        r"cat /etc/dnsmasq\.d/[a-zA-Z0-9._-]", #raw string
        r"cut -d ',' -f1 /etc/dnsmasq.d/[a-zA-Z0-9._-] | sort -f | uniq -di",
        r"cut -d ',' -f2 /etc/dnsmasq.d/[a-zA-Z0-9._-] | sort | uniq -d", 
        "sudo systemctl restart dnsmasq"
    ]
    
    # Vérification exacte
    if cmd in allowed_commands:
        return True

    dangerous_chars = ['&', ';', '>', '<', '`', '{', '}', '|']

    has_dangerous_char = False
    
    # Cas spéciaux pour sed et grep avec wildcards
    if cmd.startswith("sudo sed ") and cmd.endswith("/etc/dnsmasq.d/[a-zA-Z0-9._-]"):
        
        for char in dangerous_chars:
            if char in cmd:
                has_dangerous = True
                break

    if not has_dangerous_char:
        return True


    if cmd.startswith("grep ") and cmd.endswith("/etc/dnsmasq.d/[a-zA-Z0-9._-]"):
        has_dangerous_char = False
        for char in dangerous_char:
            if char in cmd:
                has_dangerous_char = True
                break

    if not has_dangerous_char:
        return True
    
    
    return False

def main():
    # Récupère la commande depuis SSH_ORIGINAL_COMMAND
    original_command = os.environ.get('SSH_ORIGINAL_COMMAND', '')
    
    if not original_command:
        print("Aucune commande fournie", file=sys.stderr)
        sys.exit(1)
    
    # Vérifie si la commande est autorisée
    if not is_command_allowed(original_command):
        print(f"Commande non autorisee: {original_command}", file=sys.stderr)
        sys.exit(1)
    
    # Exécute la commande
    try:
        #option shell execute via le shell systeme, capture_output=False
        result = subprocess.run(original_command, shell=True, capture_output=False)
        sys.exit(result.returncode) #termine avec le meme code de retour que la commande executee
    except Exception as e:
        print(f"Erreur lors de l'execution: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
