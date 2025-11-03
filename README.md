# PAUL: Portfolio Allocation Using Legislation

PAUL est une application web alimentée par IA qui analyse des documents législatifs (projets de loi, lois, réglementations) pour évaluer leur impact sur les entreprises du S&P 500 et fournir des recommandations d’allocation de portefeuille. Elle traite les fichiers uploadés (PDF, TXT, HTML, XML), extrait les informations pertinentes via des agents IA, interroge une base SQLite sur les données entreprises, et génère des insights structurés sur les expositions, impacts et actions suggérées (buy/sell/hold).

Le système utilise **AWS Bedrock** pour l’inférence IA (via des prompts personnalisés) et **Flask** pour le serveur web. L’interface frontend est simple (HTML/CSS/JS) pour uploader des documents et visualiser les résultats.

---

## Fonctionnalités
- Upload de documents législatifs dans plusieurs formats.
- Analyse IA des thèmes réglementaires, portées et impacts.
- Requêtes en base de données sur les secteurs, zones géographiques et opérations des entreprises.
- Recommandations d’ajustement de portefeuille basées sur les impacts du texte.
- Hébergé sur AWS pour la scalabilité.

---

## Prérequis
- **Python 3.8+** : Requis pour exécuter l’application Flask.
- **Compte AWS** : Avec accès à **Bedrock Runtime** (région : `us-west-2`).
- **SQLite** : Base de données locale (`paul.db`). Aucun serveur externe requis.
- **Dépendances** : Voir section installation.
- Pour le déploiement : Une instance **EC2** ou équivalent.

---

## Installation

1. **Cloner le dépôt** :
   ```bash
   git clone <votre-url-repo>
   cd paul
   ```

2. **Créer un environnement virtuel** (recommandé) :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows : venv\Scripts\activate
   ```

3. **Installer les dépendances** :
   ```bash
   pip install flask boto3 requests beautifulsoup4 PyPDF2
   ```

4. **Configurer les identifiants AWS** :
   ```bash
   pip install awscli
   aws configure
   ```
   Saisissez :
   - AWS Access Key ID
   - AWS Secret Access Key
   - Région : `us-west-2`
   - Format de sortie : `json`

   **Important** : Le rôle/utilisateur doit avoir les **permissions Bedrock**.

---

## Permissions AWS Bedrock (OBLIGATOIRES)

Pour que le serveur fonctionne sur AWS, **l’utilisateur ou le rôle IAM attaché à l’instance EC2** doit disposer des permissions necessaire pour acceder aux modèles Bedrock.

### Étapes :
1. Allez dans **IAM → Politiques → Créer une politique**.
2. Collez le JSON ci-dessus.
3. Nommez-la par exemple `BedrockAccessForPAUL`.
4. Attachez cette politique au **rôle IAM de l’instance EC2** ou à l’utilisateur exécutant le code.

> **Sans ces permissions, l’appel à `boto3.client("bedrock-runtime")` échouera avec `AccessDeniedException`.**

---

## Initialisation de la base de données

La base `paul.db` doit être créée et peuplée manuellement.

```python
import sqlite3

conn = sqlite3.connect('paul.db')
c = conn.cursor()

# Création des tables
c.execute('''CREATE TABLE IF NOT EXISTS company (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    name TEXT,
    marketcap REAL,
    price REAL,
    description TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS zone (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)''')

c.execute('''CREATE TABLE IF NOT EXISTS secteur (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)''')

c.execute('''CREATE TABLE IF NOT EXISTS companysectors (
    id_company INTEGER,
    id_secteur INTEGER,
    PRIMARY KEY (id_company, id_secteur),
    FOREIGN KEY (id_company) REFERENCES company(id),
    FOREIGN KEY (id_secteur) REFERENCES secteur(id)
)''')

c.execute('''CREATE TABLE IF NOT EXISTS companyzones (
    id_company INTEGER,
    id_zone INTEGER,
    description TEXT,
    PRIMARY KEY (id_company, id_zone),
    FOREIGN KEY (id_company) REFERENCES company(id),
    FOREIGN KEY (id_zone) REFERENCES zone(id)
)''')

c.execute('''CREATE TABLE IF NOT EXISTS TenK (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business TEXT,
    riskFactors TEXT,
    commentary TEXT,
    marketRisk TEXT,
    issuedDate TEXT,
    id_company INTEGER,
    FOREIGN KEY (id_company) REFERENCES company(id)
)''')

conn.commit()
conn.close()
```

> **Peuplez la base** avec les entreprises, secteurs et pays via les fonctions de `database.py` (`insert_company`, `insert_zone`, etc.).

---

## Lancer localement

```bash
python main.py
```

Accédez à : `http://localhost`

---

## Déploiement sur AWS (EC2)

### 1. Lancer une instance EC2
- **AMI** : Amazon Linux 2 ou Ubuntu
- **Type** : `t2.micro` (éligible free tier)
- **Groupe de sécurité** :
  - HTTP (80) → `0.0.0.0/0`
  - SSH (22) → votre IP
- **Rôle IAM** : Attachez le rôle avec la politique **BedrockAccessForPAUL**

### 2. Se connecter & installer
```bash
ssh -i votre-cle.pem ec2-user@<IP-PUBLIQUE>
```

```bash
sudo yum update -y
sudo yum install python3 git -y
git clone <votre-repo>
cd paul
python3 -m venv venv
source venv/bin/activate
pip install flask boto3 requests beautifulsoup4 PyPDF2
```

### 3. Configurer AWS CLI (si pas de rôle IAM)
```bash
aws configure
```

### 4. Lancer l’application
```bash
nohup python main.py &
```

> Pour la production, utilisez **Supervisor** ou **systemd**.

---

## Utilisation
1. Allez sur `http://<IP-EC2>`
2. Glissez-déposez un document législatif.
3. L’IA analyse → affiche les entreprises **à forte exposition** avec :
   - **Action** (buy/sell)
   - **Niveau d’exposition**
   - **Justification**

---

## Dépannage
| Problème | Solution |
|--------|---------|
| `AccessDeniedException` Bedrock | Vérifiez les **permissions IAM** |
| Base de données vide | Peuplez `zone`, `secteur`, `company` |
| Fichier non parsé | Vérifiez format (PDF corrompu, XML malformé) |
| Port 80 bloqué | Ouvrez-le dans le groupe de sécurité |

