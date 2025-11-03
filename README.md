
# 🧠 P.A.U.L — Portfolio Allocation Using Legislature

P.A.U.L (Portfolio Allocation Using Legislature) is a Flask web app that reads and analyzes legislative documents (laws, bills, or regulations) to assess their impact on companies, sectors, and investment portfolios.  
It uses AWS Bedrock’s LLMs to perform multi-step reasoning through four specialized agents.

---

## 📁 Project Structure

```

.
├── main.py              # Flask backend
├── prompters.py         # LLM prompts & agent logic
├── template/
│   └── index.html
├── database.py          # Database helper (user-provided)
├── static/
│   ├── style.css
│   └── script.js
└── README.md

````

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/your-username/paul-llm.git
cd paul-llm
````

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install flask boto3 PyPDF2 beautifulsoup4
```

> Optional: install `lxml` if you need faster XML parsing.

---

## 🔑 AWS Bedrock Configuration

This app uses **Amazon Bedrock** through the `boto3` SDK to access the model `openai.gpt-oss-120b-1:0`.

Configure your AWS credentials:

```bash
aws configure
```

Use:

* **Region:** `us-west-2`
* **Access Key ID / Secret Access Key:** credentials from an IAM user with Bedrock permissions

Or set environment variables manually:

```bash
export AWS_ACCESS_KEY_ID="YOUR_KEY"
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET"
export AWS_DEFAULT_REGION="us-west-2"
```

---

## 🧩 Database Setup

You must provide a file named `database.py` implementing these functions:

```python
def get_countries():
    return [("United States",), ("France",), ("China",)]

def get_sectors():
    return [("Technology",), ("Energy",), ("Finance",)]

def match_secteur(sectors, countries):
    return [("AAPL", "Apple Inc.", "Technology")]

def match_zone(sectors, countries):
    return [("AAPL", "USA", "Consumer electronics")]
```

These functions link countries and sectors to company data used during analysis.

---

## 🚀 Run the Application

### Start the Flask app:

```bash
python main.py
```

Then open your browser at:

```
http://localhost/
```

> Default port: **80**
> To change it, edit the last line in `main.py`:
>
> ```python
> app.run(host="0.0.0.0", port=5000)
> ```

---

## 🧮 How It Works

1. Upload a **bill** in `.pdf`, `.txt`, `.html`, or `.xml` format.
2. The backend:

   * Extracts and cleans text.
   * Passes it through four analysis agents:

     * **P** → Policy understanding (`agent_p`)
     * **A** → Company impact (`agent_a`)
     * **U** → Upstream/downstream impact (`agent_u`)
     * **L** → Investment strategy synthesis (`agent_l`)
3. The result (JSON) is returned and displayed in the browser.

---

## 🧠 Agent Summary

| Agent     | Purpose                              |
| --------- | ------------------------------------ |
| `agent_p` | Parses and structures the law        |
| `agent_a` | Evaluates company-level exposure     |
| `agent_u` | Analyzes supplier/client propagation |
| `agent_l` | Synthesizes portfolio strategy       |

---

## 💡 Frontend

`index.html` provides a minimal UI:

* Drag-and-drop file upload
* Displays results in a table with **Ticker**, **Action**, **Exposure**, and **Justification**

You can customize styles and behavior in `/static/style.css` and `/static/script.js`.

---

## 🧰 Troubleshooting

| Problem                    | Solution                                              |
| -------------------------- | ----------------------------------------------------- |
| `File could not be parsed` | Ensure it’s a valid PDF/TXT/HTML/XML file.            |
| AWS error                  | Check Bedrock region and IAM permissions.             |
| Flask port conflict        | Change the port in `main.py`.                         |
| Database missing           | Add a `database.py` file with the required functions. |

---

## 📜 License

This project is released under the **MIT License**.
You are free to use, modify, and distribute it.


