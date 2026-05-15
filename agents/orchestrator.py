import json
import os
import sys

from agents.agent_suggest import suggest_countries
from agents.agent_program import generate_program
from agents.agent_email import send_email


def run():
    print("=== Tour du Monde en Famille — Orchestrateur ===")

    print("\n[1/4] Suggestion de pays...")
    countries = suggest_countries()
    print(f"  Proposés : {', '.join(countries)}")
    chosen = countries[0]
    print(f"  Choisi   : {chosen}")

    print(f"\n[2/4] Génération du programme pour {chosen}...")
    program = generate_program(chosen)
    print(f"  Semaine du {program['week_start']}")

    print("\n[3/4] Mise à jour de l'historique...")
    with open("data/history.json", encoding="utf-8") as f:
        history = json.load(f)
    history.append(chosen)
    with open("data/history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    # Archive the outgoing program before it gets replaced
    try:
        with open("data/archive.json", encoding="utf-8") as f:
            archive = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        archive = []
    if not any(e.get("week_start") == program.get("week_start") for e in archive):
        archive.insert(0, program)
        with open("data/archive.json", "w", encoding="utf-8") as f:
            json.dump(archive, f, ensure_ascii=False, indent=2)

    print(f"  {len(history)} pays explorés au total")

    print("\n[4/4] Envoi de l'email récap...")
    send_email(program)

    print("\n=== Terminé avec succès ! ===")


if __name__ == "__main__":
    run()
