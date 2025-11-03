# PAUL: Portfolio Allocation Using Legislation

PAUL is an AI-powered web application that analyzes legislative documents (bills, laws, regulations) to assess their impact on S&P 500 companies and provide portfolio allocation recommendations. It processes uploaded files (PDF, TXT, HTML, XML), extracts relevant information using AI agents, queries a SQLite database for company data, and outputs structured insights on company exposures, impacts, and suggested actions (buy/sell/hold).

The system uses AWS Bedrock for AI inference (via custom prompts and models) and Flask for the web server. The frontend is a simple HTML/CSS/JS interface for uploading documents and viewing results.

## Features
- Upload legislative documents in various formats.
- AI-driven analysis of regulatory themes, scopes, and impacts.
- Database queries for company sectors, geographies, and operations.
- Recommendations for portfolio adjustments based on bill impacts.
- Hosted on AWS for scalability.

## Prerequisites
- **Python 3.8+**: Required for running the Flask app.
- **AWS Account**: With access to Bedrock Runtime (region: us-west-2). You'll need IAM credentials with permissions for `bedrock-runtime`.
- **SQLite**: The app uses a local SQLite database (`paul.db`). No external DB server needed.
- **Dependencies**: Listed in the installation section.
- For deployment: An AWS EC2 instance or similar for hosting the web server.

## Installation

1. **Clone the Repository**:
   ```
   git clone <your-repo-url>
   cd paul
   ```

2. **Set Up a Virtual Environment** (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   Install the required Python packages:
   ```
   pip install flask boto3 requests beautifulsoup4 PyPDF2
   ```
   - `flask`: Web framework.
   - `boto3`: AWS SDK for Bedrock integration.
   - `requests`: HTTP requests (used in database.py).
   - `beautifulsoup4`: HTML parsing.
   - `PyPDF2`: PDF extraction.

   Note: Built-in modules like `sqlite3`, `json`, `os`, `re`, `io`, and `xml.etree.ElementTree` are already available in Python.

4. **Configure AWS Credentials**:
   - Install the AWS CLI if not already: `pip install awscli`.
   - Configure credentials:
     ```
     aws configure
     ```
     Enter your AWS Access Key ID, Secret Access Key, region (`us-west-2`), and output format (`json`).
   - Ensure your IAM role/user has permissions for Bedrock Runtime (e.g., `bedrock:InvokeModel`).

5. **Set Up the Database**:
   The app uses a SQLite database (`paul.db`) for storing company, sector, and zone data. The schema is not auto-created in the code, so you'll need to initialize it manually.

   - Create the database file: Run Python interactively or create a script to execute the following SQL:
     ```python
     import sqlite3

     conn = sqlite3.connect('paul.db')
     c = conn.cursor()

     # Create tables (inferred from database.py functions)
     c.execute('''
     CREATE TABLE IF NOT EXISTS company (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         ticker TEXT NOT NULL,
         name TEXT,
         marketcap REAL,
         price REAL,
         description TEXT
     )
     ''')

     c.execute('''
     CREATE TABLE IF NOT EXISTS zone (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         name TEXT UNIQUE NOT NULL
     )
     ''')

     c.execute('''
     CREATE TABLE IF NOT EXISTS secteur (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         name TEXT UNIQUE NOT NULL
     )
     ''')

     c.execute('''
     CREATE TABLE IF NOT EXISTS companysectors (
         id_company INTEGER,
         id_secteur INTEGER,
         FOREIGN KEY (id_company) REFERENCES company(id),
         FOREIGN KEY (id_secteur) REFERENCES secteur(id),
         PRIMARY KEY (id_company, id_secteur)
     )
     ''')

     c.execute('''
     CREATE TABLE IF NOT EXISTS companyzones (
         id_company INTEGER,
         id_zone INTEGER,
         description TEXT,
         FOREIGN KEY (id_company) REFERENCES company(id),
         FOREIGN KEY (id_zone) REFERENCES zone(id),
         PRIMARY KEY (id_company, id_zone)
     )
     ''')

     c.execute('''
     CREATE TABLE IF NOT EXISTS TenK (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         business TEXT,
         riskFactors TEXT,
         commentary TEXT,
         marketRisk TEXT,
         issuedDate TEXT,
         id_company INTEGER,
         FOREIGN KEY (id_company) REFERENCES company(id)
     )
     ''')

     conn.commit()
     conn.close()
     ```
   - Populate the database: Use the functions in `database.py` (e.g., `insert_zone`, `insert_secteur`, `insert_company`) to add data. For example, add sectors and countries from your data sources (e.g., S&P 500 companies). The app assumes pre-populated data for queries like `get_countries()` and `get_sectors()`.

## Running Locally
1. Start the Flask app:
   ```
   python main.py
   ```
   The server will run on `http://0.0.0.0:80` (or `http://localhost:80`).

2. Access the app:
   - Open a browser and go to `http://localhost`.
   - Upload a legislative document (PDF, TXT, HTML, or XML) via the drop zone.
   - The app will process it using AI agents and display results in a table.

Note: Ensure Bedrock has access to the model specified (`openai.gpt-oss-120b-1:0`). If this is a custom or placeholder model, replace it in `prompters.py` with a valid Bedrock model ID (e.g., `anthropic.claude-v2`).

## Deploying to AWS
To host the web server on AWS (e.g., using EC2):

1. **Launch an EC2 Instance**:
   - Choose Amazon Linux 2 or Ubuntu.
   - Instance type: t2.micro (free tier eligible) or larger.
   - Security Group: Allow inbound HTTP (port 80) and SSH (port 22).
   - Attach an IAM role with Bedrock permissions (or configure credentials on the instance).

2. **Set Up the Instance**:
   - SSH into the instance: `ssh -i your-key.pem ec2-user@your-instance-ip`.
   - Update packages: `sudo yum update -y` (Amazon Linux) or `sudo apt update && sudo apt upgrade -y` (Ubuntu).
   - Install Python and Git: `sudo yum install python3 git -y` or `sudo apt install python3 python3-venv git -y`.
   - Clone the repo: `git clone <your-repo-url> && cd paul`.
   - Set up virtual env and install deps (as in Installation section).

3. **Configure AWS Credentials**:
   - If not using an IAM role, run `aws configure` on the instance.

4. **Run the App**:
   - For production, use a process manager like Supervisor or systemd.
     - Install Supervisor: `sudo yum install supervisor -y` or `sudo apt install supervisor -y`.
     - Create `/etc/supervisord.d/paul.ini`:
       ```
       [program:paul]
       command=/path/to/venv/bin/python /path/to/paul/main.py
       directory=/path/to/paul
       autorestart=true
       ```
     - Start: `sudo supervisord -c /etc/supervisord.conf` and `sudo supervisorctl reload`.
   - Alternatively, run in background: `nohup python main.py &`.

5. **Access the App**:
   - Go to `http://your-instance-public-ip`.
   - For HTTPS, set up NGINX/Apache as a reverse proxy and obtain an SSL cert (e.g., via Let's Encrypt).

6. **Optional: Auto-Scaling and Domain**:
   - Use Elastic Beanstalk for easier deployment.
   - Point a domain (via Route 53) to the EC2 IP.

## Usage
- Upload a document: The app cleans the text, runs AI agents (P: Profile, A: Assess, U: Upstream/Downstream, L: Leverage/Synthesize), and returns JSON with company recommendations.
- Results: Table shows high-exposure companies with actions (buy/sell), exposure level, and reasons. A summary is displayed below.

## Troubleshooting
- **Database Errors**: Ensure `paul.db` exists and is populated. Check table schemas match the queries in `database.py`.
- **Bedrock Errors**: Verify model ID and region. Test with `boto3` client manually.
- **File Parsing Issues**: Ensure uploaded files are valid; unsupported formats return errors.
- **AWS Costs**: Monitor Bedrock invocations and EC2 usage to avoid unexpected bills.

## Contributing
Fork the repo, make changes, and submit a PR. Focus on improving AI prompts, adding DB init scripts, or enhancing frontend.
