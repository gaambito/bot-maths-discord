import os
import requests
import random
import json
import argparse
from datetime import datetime

# --- CONFIGURATION & FICHIER DE DONNÉES ---
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
DATA_FILE = "data.json"

# --- LOGIQUE MATHÉMATIQUE AVEC MÉTHODE ---

def generer_methodes(a, b, op, reponse):
    """Génère une explication simplifiée pour le calcul mental."""
    if op == '+':
        if b < 10 or a < 100:
            return f"On décompose le plus petit nombre : {a} + {b // 10 * 10} = {a + b // 10 * 10}. Puis on ajoute le reste ({b % 10}) : {reponse}."
        else:
            return f"On arrondit ou on décompose : {a} + {b} = {reponse}."
    
    elif op == '-':
        if b < 10:
             return f"On retire d'abord les unités : {a} - {b} = {reponse}."
        else:
            # Méthode du "complément à..." ou de l'arrondi pour la soustraction
            b_arrondi = (b // 10 + 1) * 10 if b % 10 > 5 else b // 10 * 10
            if a > 100 or b > 20:
                 return f"Méthode de l'arrondi : on fait {a} - {b_arrondi} = {a - b_arrondi}, puis on ajuste pour trouver {reponse}."
            return f"On décompose : {a} - {b // 10 * 10} = {a - b // 10 * 10}. Puis on retire le reste ({b % 10}) : {reponse}."

    elif op == '*':
        if a in (11, 12) or b in (11, 12):
            return f"Règle des 11/12 ou décomposition : {a} x {b} = {reponse}."
        elif a % 10 == 0 or b % 10 == 0:
            return f"On multiplie les chiffres sans le zéro ({a // 10 if a % 10 == 0 else a} x {b // 10 if b % 10 == 0 else b}), et on ajoute les zéros : {reponse}."
        else:
            return f"Décomposition simple : {a} x {b // 2} + {a} x {b // 2} (+ si impair). Le résultat est {reponse}."
            
    elif op == '/':
        return f"La division est l'inverse de la multiplication : {reponse} x {b} = {a}."
    
    return f"Le résultat est {reponse}."

def generer_calcul(niveau):
    # Logique de génération des nombres (adaptée de la version précédente)
    op = random.choice(['+', '-', '*', '/'])
    a, b, reponse = 0, 0, 0
    
    if niveau == 'simple':
        if op == '+': a, b = random.randint(1, 50), random.randint(1, 50); reponse = a + b
        elif op == '-': a = random.randint(10, 50); b = random.randint(1, a); reponse = a - b
        elif op == '*': a, b = random.randint(2, 9), random.randint(2, 9); reponse = a * b
        elif op == '/': b = random.randint(2, 9); reponse = random.randint(2, 9); a = b * reponse
    elif niveau == 'moyen':
        if op == '+': a, b = random.randint(20, 99), random.randint(20, 99); reponse = a + b
        elif op == '-': a = random.randint(50, 99); b = random.randint(10, a - 10); reponse = a - b
        elif op == '*':
            if random.random() > 0.5: a, b = random.randint(11, 15), random.randint(2, 9) # Tables 11-15
            else: a, b = random.randint(2, 9) * 10, random.randint(2, 9) # Dizaines
            reponse = a * b
        elif op == '/': b = random.randint(3, 9); reponse = random.randint(11, 20); a = b * reponse
    elif niveau == 'difficile':
        if op == '+': a, b = random.randint(100, 400), random.randint(50, 250); reponse = a + b
        elif op == '-': a = random.randint(150, 500); b = random.randint(50, 150); reponse = a - b
        elif op == '*': a, b = random.randint(11, 15), random.randint(6, 12); reponse = a * b
        elif op == '/': b = random.randint(4, 12); reponse = random.randint(15, 30); a = b * reponse

    symbole = {'+': '+', '-': '-', '*': 'x', '/': '÷'}[op]
    question = f"{a} {symbole} {b}"
    method = generer_methodes(a, b, op, reponse)
    
    return {'q': question, 'r': reponse, 'm': method, 'lvl': niveau}

def generer_defi_complet():
    structure = [('simple', 3), ('moyen', 4), ('difficile', 3)]
    defi_complet = []
    
    for niveau, quantite in structure:
        for _ in range(quantite):
            defi_complet.append(generer_calcul(niveau))
    
    return defi_complet

# --- GESTION DES MESSAGES ET ENVOI ---

def envoyer_message(content):
    if not WEBHOOK_URL:
        print("Erreur : L'URL du Webhook est manquante.")
        return False

    data = {"content": content}
    response = requests.post(WEBHOOK_URL, json=data)

    if response.status_code == 204:
        print("✅ Message envoyé avec succès !")
        return True
    else:
        print(f"❌ Erreur {response.status_code}: {response.text}")
        return False

def mode_challenge():
    defi = generer_defi_complet()
    
    # 1. Sauvegarde des données pour la correction
    with open(DATA_FILE, 'w') as f:
        json.dump(defi, f)
    print(f"💾 Données sauvegardées dans {DATA_FILE}")

    # 2. Construction du message du défi (questions uniquement)
    date_jour = datetime.now().strftime("%d/%m/%Y")
    exercices_msg = []
    numero = 1

    exercices_msg.append(f"## 📅 Défi Calcul du {date_jour} 🧠\n")
    exercices_msg.append("*Objectif : Fais-les de tête, puis vérifie.*\n")
    
    current_level = ""
    for item in defi:
        if item['lvl'] != current_level:
            emoji = {'simple': '🟢', 'moyen': '🟠', 'difficile': '🔴'}[item['lvl']]
            exercices_msg.append(f"\n_Niveau {item['lvl'].capitalize()} {emoji}_")
            current_level = item['lvl']

        exercices_msg.append(f"**{numero}.** {item['q']} = ?")
        numero += 1

    message = "\n".join(exercices_msg)
    message += f"\n\n--- \n**Les corrections arriveront dans 2 heures !** ⏱️"
    
    # 3. Envoi
    return envoyer_message(message)

def mode_correction():
    # 1. Lecture des données sauvegardées
    if not os.path.exists(DATA_FILE):
        print(f"❌ Erreur : Fichier de données {DATA_FILE} non trouvé pour la correction.")
        return False
        
    with open(DATA_FILE, 'r') as f:
        defi = json.load(f)
        
    # 2. Construction du message de correction
    corrections_msg = []
    numero = 1
    corrections_msg.append("## ✅ Correction du Défi d'aujourd'hui\n")
    corrections_msg.append("Voici les réponses et la méthode de calcul mental suggérée pour chaque exercice.\n")

    current_level = ""
    for item in defi:
        if item['lvl'] != current_level:
            emoji = {'simple': '🟢', 'moyen': '🟠', 'difficile': '🔴'}[item['lvl']]
            corrections_msg.append(f"\n_Niveau {item['lvl'].capitalize()} {emoji}_")
            current_level = item['lvl']

        corrections_msg.append(f"**{numero}.** {item['q']} = **{item['r']}**")
        corrections_msg.append(f"> Méthode : {item['m']}")
        numero += 1

    message = "\n".join(corrections_msg)
    
    # 3. Envoi
    return envoyer_message(message)

# --- POINT D'ENTRÉE ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bot de calcul mental Discord.")
    parser.add_argument('mode', choices=['challenge', 'correction'], help="Mode d'exécution : 'challenge' (envoi du défi) ou 'correction' (envoi des réponses).")
    args = parser.parse_args()

    if args.mode == 'challenge':
        mode_challenge()
    elif args.mode == 'correction':
        mode_correction()
