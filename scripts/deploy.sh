#!/bin/bash
# deploy.sh — déployer une mise à jour sur le Pi après git push
# Usage : bash scripts/deploy.sh

set -e

PI="hbouamar@myRasp.local"

echo "→ git pull sur le Pi..."
ssh "$PI" "git -C ~/family-world-tour pull"

echo "✅ Déployé sur le Pi."
echo "   Local  : http://myRasp.local:8081"
echo "   Public : https://family.krousty.uk"
