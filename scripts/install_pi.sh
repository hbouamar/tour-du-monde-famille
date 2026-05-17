#!/bin/bash
# install_pi.sh — à lancer UNE FOIS depuis le Mac pour configurer le Pi
# Usage : bash scripts/install_pi.sh

set -e

PI="hbouamar@myRasp.local"
REPO="https://github.com/hbouamar/tour-du-monde-famille.git"
TUNNEL_ID="2f8948fe-5623-4a0f-95d0-d6a44aa4875e"
MAC_PROJECT="$HOME/Projects/family-world-tour"

echo "=== 1. Dépendances système ==="
ssh "$PI" "sudo apt-get update -q && sudo apt-get install -y python3-venv python3-pip git nginx -q"

echo "=== 2. Clonage du repo ==="
ssh "$PI" "
  if [ -d ~/family-world-tour ]; then
    echo 'Repo existant — git pull'
    git -C ~/family-world-tour pull
  else
    git clone $REPO ~/family-world-tour
  fi
  mkdir -p ~/family-world-tour/data ~/family-world-tour/logs
"

echo "=== 3. Venv Python + dépendances ==="
ssh "$PI" "
  cd ~/family-world-tour
  python3 -m venv venv
  venv/bin/pip install --upgrade pip -q
  venv/bin/pip install -r requirements.txt -q
"

echo "=== 4. Copie config.json ==="
if [ -f "$MAC_PROJECT/config.json" ]; then
  scp "$MAC_PROJECT/config.json" "$PI:~/family-world-tour/config.json"
else
  echo "⚠️  config.json introuvable sur le Mac. Copie manuelle requise :"
  echo "   cp config.json.example config.json  # puis éditer"
  echo "   scp config.json $PI:~/family-world-tour/config.json"
fi

echo "=== 5. Config nginx ==="
# nginx tourne en www-data — il doit pouvoir traverser le home
ssh "$PI" "chmod o+x /home/hbouamar"
ssh "$PI" "sudo cp ~/family-world-tour/scripts/nginx/family-world-tour.conf /etc/nginx/sites-available/family-world-tour"
ssh "$PI" "sudo ln -sf /etc/nginx/sites-available/family-world-tour /etc/nginx/sites-enabled/family-world-tour"
ssh "$PI" "sudo nginx -t && sudo systemctl reload nginx"

echo "=== 6. Cloudflare tunnel — ajout hostname family.krousty.uk ==="
ssh "$PI" "cat > ~/.cloudflared/config.yml" << EOF
tunnel: $TUNNEL_ID
credentials-file: /home/hbouamar/.cloudflared/$TUNNEL_ID.json

ingress:
  - hostname: pronote.krousty.uk
    service: http://localhost:8080
  - hostname: family.krousty.uk
    service: http://localhost:8081
  - service: http_status:404
EOF

echo "=== 7. Services systemd (timer agents) ==="
ssh "$PI" "mkdir -p ~/.config/systemd/user && loginctl enable-linger \$USER"
scp "$MAC_PROJECT/scripts/systemd/"*.service "$PI:~/.config/systemd/user/"
scp "$MAC_PROJECT/scripts/systemd/"*.timer   "$PI:~/.config/systemd/user/"
ssh "$PI" "
  systemctl --user daemon-reload
  systemctl --user enable family-agents.timer
  systemctl --user start  family-agents.timer
"

echo "=== 8. Redémarrage tunnel Cloudflare ==="
ssh "$PI" "systemctl --user restart pronote-tunnel"

echo ""
echo "✅ Installation terminée !"
echo "   Local  : http://myRasp.local:8081"
echo "   Public : https://family.krousty.uk  (après DNS Cloudflare)"
echo ""
echo "⚠️  DNS Cloudflare — à faire manuellement dans le dashboard :"
echo "   Type : CNAME"
echo "   Nom  : family"
echo "   Cible: $TUNNEL_ID.cfargotunnel.com"
echo "   Proxy: activé (nuage orange)"
echo ""
echo "Vérifie les services avec :"
echo "   ssh $PI 'systemctl --user status family-agents.timer && sudo systemctl status nginx'"
