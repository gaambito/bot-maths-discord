import os
import requests
import random
from datetime import datetime

# --- CONFIGURATION ---
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# --- LOGIQUE MATHÉMATIQUE ---
def generer_calcul(niveau):
    # Choix de l'opération (poids égaux)
    op = random.choice(['+', '-', '*', '/'])
    
    a, b, reponse = 0, 0, 0

    # --- NIVEAU SIMPLE (Réflexes, tables 1-9) ---
    if niveau == 'simple':
        if op == '+':
            a = random.randint(1, 50)
            b = random.randint(1, 50)
            reponse = a + b
        elif op == '-':
            a = random.randint(10, 50)
            b = random.randint(1, a) # Pas de négatifs
            reponse = a - b
        elif op == '*':
            a = random.randint(2, 9)
            b = random.randint(2, 9)
            reponse = a * b
        elif op == '/':
            b = random.randint(2, 9)      # Diviseur
            reponse = random.randint(2, 9) # Résultat attendu
            a = b * reponse               # On calcule le dividende pour tomber juste
    
    # --- NIVEAU MOYEN (Retenues, tables 11-15, dizaines) ---
    elif niveau == 'moyen':
        if op == '+':
            a = random.randint(20, 99)
            b = random.randint(20, 99)
            reponse = a + b
        elif op == '-':
            a = random.randint(50, 99)
            b = random.randint(10, a - 10)
            reponse = a - b
        elif op == '*':
            # Soit table 11-15, soit multiplication par des dizaines (ex: 40 * 6)
            if random.random() > 0.5:
                a = random.randint(11, 15)
                b = random.randint(2, 9)
            else:
                a = random.randint(2, 9) * 10
                b = random.randint(2, 9)
            reponse = a * b
        elif op == '/':
            b = random.randint(3, 9)
            reponse = random.randint(11, 20) # Résultat entre 11 et 20
            a = b * reponse

    # --- NIVEAU DIFFICILE (3 chiffres, calculs lourds) ---
    elif niveau == 'difficile':
        if op == '+':
            a = random.randint(100, 400)
            b = random.randint(50, 250)
            reponse = a + b
        elif op == '-':
            a = random.randint(150, 500)
            b = random.randint(50, 150)
            reponse = a - b
        elif op == '*':
            a = random.randint(11, 15)
            b = random.randint(6, 12) # Grosses multiplications
            reponse = a * b
        elif op == '/':
            b = random.randint(4, 12)
            reponse = random.randint(15, 30) # Gros résultats
            a = b * reponse

    # Mise en forme du symbole pour l'affichage
    symbole = {'+': '+', '-': '-', '*': 'x', '/': '÷'}[op]
    question = f"{a} {symbole} {b}"
    return question, reponse

# --- GÉNÉRATION DES 10 EXERCICES ---
structure = [
    ('simple', 3),    # 3 exercices simples
    ('moyen', 4),     # 4 exercices moyens
    ('difficile', 3)  # 3 exercices difficiles
]

exercices_msg = []
corrections_msg = []
numero = 1

for niveau, quantite in structure:
    # Petit titre de section pour aérer
    emoji_niveau = {'simple': '🟢', 'moyen': '🟠', 'difficile': '🔴'}[niveau]
    titre_section = f"\n_Niveau {niveau.capitalize()} {emoji_niveau}_"
    exercices_msg.append(titre_section)
    corrections_msg.append(titre_section)
    
    for _ in range(quantite):
        q, r = generer_calcul(niveau)
        
        # Ligne exercice
        exercices_msg.append(f"**{numero}.** {q} = ?")
        
        # Ligne correction (avec Spoiler ||...||)
        corrections_msg.append(f"**{numero}.** {q} = || **{r}** ||")
        
        numero += 1

# --- CONSTRUCTION DU MESSAGE DISCORD ---
date_jour = datetime.now().strftime("%d/%m/%Y")
message_final = f"""
## 📅 Défi Calcul du {date_jour} 🧠

Voici tes 10 calculs du jour ! 
*Objectif : Fais-les de tête ou sur un brouillon, puis vérifie.*

{chr(10).join(exercices_msg)}

---
⬇️ **CORRECTIONS (Clique sur les carrés noirs)** ⬇️

{chr(10).join(corrections_msg)}

*À demain !* 🚀
"""

# --- ENVOI ---
if not WEBHOOK_URL:
    print("Erreur : L'URL du Webhook est manquante dans les secrets GitHub.")
    exit(1)

data = {"content": message_final}
response = requests.post(WEBHOOK_URL, json=data)

if response.status_code == 204:
    print("✅ Message envoyé avec succès !")
else:
    print(f"❌ Erreur {response.status_code}: {response.text}")
