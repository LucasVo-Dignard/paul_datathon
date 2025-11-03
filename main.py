from flask import Flask, render_template, request, jsonify
import json
from prompters import agent_p, agent_a, agent_u, agent_l
import os
import database as db
from io import BytesIO
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET


def extract_text(element):
    """Recursively extract text from XML elements."""
    texts = []
    if element.text:
        texts.append(element.text.strip())
    for child in element:
        texts.extend(extract_text(child))
    if element.tail:
        texts.append(element.tail.strip())
    return texts


def cleanup(file):
    _, ext = os.path.splitext(file.filename)
    ext = ext.lower().lstrip('.')  # 'pdf', 'html', 'txt', 'xml', etc.

    raw_bytes = file.read()
    if ext == 'pdf':
        from PyPDF2 import PdfReader
        reader = PdfReader(BytesIO(raw_bytes))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    elif ext == 'html':
        soup = BeautifulSoup(raw_bytes.decode('utf-8', errors='ignore'), 'html.parser')
        return soup.get_text(separator=" ", strip=True)

    elif ext == 'xml':
        try:
            tree = ET.fromstring(raw_bytes.decode('utf-8', errors='ignore'))
            text_list = extract_text(tree)
            return " ".join(t for t in text_list if t)

        except ET.ParseError:
            return False

    elif ext == 'txt':
        return raw_bytes.decode('utf-8', errors='ignore')

    else:
        return False


def process(clean_text):
    step_p = False
    p_res = ""
    while not step_p:
        try:
            p_res = agent_p(clean_text)

            affected_sectors = [i["name"] for i in json.loads(p_res)["exposure_surfaces"]["sectors"]]
            affected_countries = [i["name"] for i in json.loads(p_res)["exposure_surfaces"]["countries"]]
            step_p = True
            print("Step P complete.")
        except Exception as e:
            print("Error at step P. Retrying.")
            print(e)

    info1 = db.match_secteur(affected_sectors, affected_countries)
    info2 = db.match_zone(affected_sectors, affected_countries)

    uses = {}
    for info in info2:
        uses[info[0]] = []
    for info in info2:
        uses[info[0]].append(f"""{info[1]}: {info[2]}""")

    q = {}
    for i in info1:
        q[i[0]] = {
            "description": i[1],
            "sector": i[2],
            "operating_countries": uses[i[0]]
        }

    step_a = False
    a_res = ""
    while not step_a:
        try:
            a_res = agent_a(p_res, q)
            step_a = True
            print("Step A complete.")
        except:
            print("Error at step A. Retrying.")

    step_u = False
    u_res = ""
    while not step_u:
        try:
            u_res = agent_u(p_res, a_res)
            step_u = True
            print("Step U complete.")
        except:
            print("Error at step U. Retrying.")

    step_l = False
    l_res = ""
    while not step_l:
        try:
            l_res = agent_l(p_res, a_res, u_res)
            json.loads(l_res)
            step_l = True
            print("Step L complete.")
        except:
            print("Error at step L. Retrying.")
    print(l_res)
    return l_res


app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'bill' not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files['bill']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    clean_text = cleanup(file)
    if not clean_text:
        return jsonify({"message": "File could not be parsed."}), 400

    return jsonify(process(clean_text))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
