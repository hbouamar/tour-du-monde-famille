import json
import os
import google.generativeai as genai


def suggest_countries() -> list[str]:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    with open("data/history.json", encoding="utf-8") as f:
        history = json.load(f)

    history_str = ", ".join(history) if history else "aucun pays pour l'instant"

    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""Tu es un expert en cultures du monde pour enfants.
Propose 3 pays différents pour un programme culturel familial hebdomadaire.
Pays déjà explorés (à éviter absolument) : {history_str}

Critères :
- Adapté à des enfants de 7 et 12 ans
- Riche culturellement (cuisine, art, musique, traditions)
- Varié (différents continents si possible)

Réponds UNIQUEMENT avec un JSON valide :
{{"pays": ["Pays1", "Pays2", "Pays3"]}}"""

    response = model.generate_content(prompt)
    text = response.text.strip()

    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    return json.loads(text)["pays"]


if __name__ == "__main__":
    countries = suggest_countries()
    print("Pays suggérés :", countries)
