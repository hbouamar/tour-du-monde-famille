# Tour du Monde en Famille 🌍

## Contexte famille
- Alice (7 ans, 8 ans le 21 avril) et Liam (presque 12 ans, 12 ans le 6 juillet)
- Programme culturel hebdomadaire : lundi → samedi

## Stack technique
- LLM : Gemini API + Grok API (pas d'API Claude)
- CI/CD : GitHub Actions (cron samedi 16h)
- Hébergement : GitHub Pages
- Persistance : fichiers JSON commités dans le repo

## Architecture
- agents/orchestrator.py : chef d'orchestre
- agents/agent_suggest.py : propose 3 pays via Gemini
- agents/agent_program.py : génère le programme semaine via Gemini
- agents/agent_email.py : rédige et envoie l'email récap via Gemini
- data/history.json : pays déjà faits
- data/current_program.json : programme semaine en cours
- data/progress.json : statut activités (todo/doing/done/skip)
- web/ : GitHub Pages - suivi des activités
