# Convertisseur / Nettoyeur de fichiers — Demo (MVP)

## Contenu
Projet Flask minimal prêt à déployer.

## Installation locale
1. Cloner le repo
2. Créer et activer un virtualenv
   python -m venv env
   source env/bin/activate
3. Installer les dépendances
   pip install -r requirements.txt
4. Copier `.env.example` en `.env` et renseigner les clés Stripe et FLASK_SECRET
5. Lancer
   python app.py

## Déploiement rapide (Render)
1. Créer un dépôt GitHub et pousser le projet
2. Sur Render : New -> Web Service -> Connect GitHub repo -> Branch main
3. Build command: `pip install -r requirements.txt`
   Start command: `gunicorn app:app`
4. Ajouter les variables d'environnement (Render Dashboard) : FLASK_SECRET, STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY
(Voir docs Render: https://render.com/docs/deploy-flask)

## Notes
- Améliorer la sécurité avant usage public (validation, tailles, authentification, quotas)
- Pour conversion lourde, envisager Celery/RQ + Redis
