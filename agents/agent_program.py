import json
import os
from datetime import datetime, timedelta
from google import genai
from agents.config import load_config

DAYS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"]


def generate_program(country: str) -> dict:
    load_config()
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    today = datetime.today()
    days_until_monday = (7 - today.weekday()) % 7 or 7
    week_start = (today + timedelta(days=days_until_monday)).strftime("%Y-%m-%d")

    prompt = f"""Crée un programme culturel hebdomadaire sur le pays : {country}
Pour une famille avec Alice (7 ans) et Liam (12 ans).
Programme du lundi au samedi (6 jours).

Pour chaque jour, propose 1 à 2 activités parmi : cuisine, art/artisanat, musique/danse, histoire/géographie, film/livre, jeux/sports traditionnels.

Réponds UNIQUEMENT avec un JSON valide :
{{
  "country": "{country}",
  "week_start": "{week_start}",
  "cultural_images": [
    {{"label": "nom français de l'élément", "wiki_en": "English_Wikipedia_page_title"}},
    {{"label": "...", "wiki_en": "..."}},
    {{"label": "...", "wiki_en": "..."}},
    {{"label": "...", "wiki_en": "..."}},
    {{"label": "...", "wiki_en": "..."}},
    {{"label": "...", "wiki_en": "..."}}
  ],
  "days": {{
    "lundi": {{
      "theme": "thème court du jour",
      "activities": [
        {{"id": "lundi_1", "title": "titre court", "description": "2-3 phrases concrètes", "type": "cuisine", "duration": "45min", "resource_query": "requête YouTube pertinente en français pour cette activité"}}
      ]
    }},
    "mardi": {{}},
    "mercredi": {{}},
    "jeudi": {{}},
    "vendredi": {{}},
    "samedi": {{}}
  }}
}}"""

    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    text = response.text.strip()

    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    program = json.loads(text)

    with open("data/current_program.json", "w", encoding="utf-8") as f:
        json.dump(program, f, ensure_ascii=False, indent=2)

    progress = {}
    for day in DAYS:
        for activity in program.get("days", {}).get(day, {}).get("activities", []):
            progress[activity["id"]] = "todo"

    with open("data/progress.json", "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

    return program


if __name__ == "__main__":
    program = generate_program("Japon")
    print(f"Programme généré pour {program['country']}, semaine du {program['week_start']}")
