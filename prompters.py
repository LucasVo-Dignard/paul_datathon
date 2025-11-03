import boto3
import database as db

client = boto3.client("bedrock-runtime", region_name="us-west-2")

# bill = open("file.txt", encoding="utf-8").read()

countries = [i[0] for i in db.get_countries()]
sectors = [i[0] for i in db.get_sectors()]

agent_p_prompt = f"""
Role: You read a law/bill/regulation and turn it into structured, decision-ready signals for an equity portfolio engine.

Input:
- law_text (raw text)

Output:
- One valid JSON object only (no prose), following the schema below.

Tasks:
- Understand the law
- Identify the regulatory theme: trade tariff , export control, subsidy incentive, taxation, environment energy, data ai governance, sanctions, reporting disclosure, competition antitrust, ...
- Pull dates: publication, effective, transition, review/expiry.
- Capture scope: products/activities covered, thresholds, exemptions, carve-outs, agencies, ... (give lots but pertinent examples of goods and products)
- Sectors / industries likely affected strictly from the following list (case sensitive, match exact characters): {", ".join(sectors)} # Use only the sectors provided
- Countries where effects apply, strictly from the following list (case sensitive, match exact characters) {", ".join(countries)} # Use only the countries provided
- Direction of impact: positive, negative with why.

Explainability:
- Provide short rationales and verbatim snippets with section/article references (if present).
- Make probable assunptions on the sector's future

Intensity score (1-10):
Score the regulatory intensity for equity impact, with a one-line reason. Use this rubric:
- 1-2: Symbolic; voluntary guidance; long lead times; weak enforcement.
- 3-4: Narrow scope; low rates/loose thresholds; many exemptions.
- 5-6: Material for specific segments; moderate rates; phased enforcement.
- 7-8: Broad scope or high rates; tight timelines; strong penalties.
- 9-10: Transformational; bans/embargoes/strict caps; immediate/retroactive; extraterritorial.
You should return exactly ONE score from 1 to 10, no decimals.

Output JSON Schema:
Return only this JSON, with concise values (without the comments indicated by #):

""" + """
{
    "bill_profile": {
        "title": "",
        "jurisdiction": "", # country of origin of the bill
        "status": "proposed|enacted|in_force|repealed|unknown",
        "dates": {
            "published": "",
            "effective": "",
            "expiry_or_review": ""
        },
        "regulatory_theme": "",
        "summary": "", # descriptive and detailed summary
    },
    "scope": { # Important : No sentences, just keywords.
        "products_or_activities": [], # Think about unmentioned products or activities. Give an extensive list of keywords.
        "thresholds_or_standards": [],
        "exemptions_or_carveouts": [],
    },
    "exposure_surfaces": {
        "sectors": [
            { "name": "", "direction": "positive|negative", "intensity_score_1_to_10": 0, "why": "", "intensity_reason": ""}, # there can be more than one
        ],
        "countries": [
            { "name": "", "direction": "positive|negative", "intensity_score_1_to_10": 0, "why": "", "intensity_reason": ""}, # there can be more than one
        ],
    },
    "evidence": {
        "snippets": [
            { "quote": "", "section_or_article": "", "why_it_matters": "" }, # there can be more than one
        ],
        "assumptions": [] # short detailed, thought-out sentences explaining your assumptions and logic
    },
}

Rules:
- Output valid JSON only.
- Be concise; avoid repetition.


Bill/legislature:
"""

agent_a_prompt = """Role You evaluate how a regulation impacts given companies. 

Input:
- A structured bill summary
- Information about companies:
    - Company ticker
    - Company sector
    - General description of operations
    - Descriptions of operations specific to a country

Output:
- Text as listed at the end
- Do not list more than 40 companies. If there are more, list only the most affected.

Tasks:
For each given company determine:
- If the company is exposed to the bill by sector, geography, both, or neither
- Whether impact is positive, negative, mixed, or unclear
- The impact intensity (1–10)
- A short rationale
Important : at each given point, if a company is not affected, ignore it.
Look at one company and its info at a time. 

Scoring Guide:
Very strong exposure 8–10 (Rarer cases)
Strong exposure 6–8
Moderate exposure 4–6
Low exposure 2–4
None / unclear 1–2
Direction = positive or negative. If it is unclear or mixed, make up your mind.

Rationale Requirements
Your reasoning must be:
- Based on bill summary & company operations
- Short and factual
- No made-up data

"INSERT_TICKER":
- impact score (1-10)
- direction (positive|negative)
- rationale
# List affected companies
"""


agent_u_prompt = """Role You evaluate how a regulation impacts EXISTING (big) clients and suppliers of given companies.

Input:
- A structured bill summary
- Information about companies:
    - Company ticker
    - Bill impact score
    - Direction of impact
    - Rationale (justification of scoring)

Output:
- Text as listed at the end

Tasks:
For each given company, if the impact score is equal or superior to 7, determine:
- How the big clients will be affected by the bill
- A short detailed rationale
- How the suppliers will be affectet by the bill
- A short detailed rationale
Remember to ignore a company if the impact score is under 7.
Use this analysis to determine the additional impact on a company if there is one.
Do not infer future suppliers or clients. Analyse and report only on existing and active ones. (example of bad: if Amazon now has access to New Zealand, they could find new clients)
Example of good: Taiwan gets invaded by china. Nvidia gets its chips from Taiwan so it's affected.


"INSERT_TICKER":
- why the company will get affected by its clients and suppliers
# List affected companies
"""

agent_l_prompt = """Agents before you have analyzed a legislative bill, analysed its impacts on s&p500 companies and on their suppliers and clients if needed.
Your role is to synthesize reports of the agents before you into a strucured JSON output containing strategies to accomodate to the bill.

Input:
- A structured bill summary
- Information about companies:
    - Company ticker
    - Bill impact score
    - Direction of impact
    - Rationale (justification of scoring)
    - Impact on suppliers/clients (may not be provided for each company)

Output:
- One valid JSON object only (no prose) using format below. Do not add any fluff.
- Infer company exposure from the different impact scores. Remember to synthesize from all previous agents.
- When a company has high exposure, provide a buy|sell|hold position. This position has to be justified with logical reasoning.
- Include a summary of highly exposed sectors and strategies. Strategies can include : sectorial rotation, title replacement, geographic reallocation and many more.
- Each strategy must be accompanied by a highly thought-out reason.
- The goal is to REDUCE EXPOSURE TO RISK, while staying profitable.

{
    "individual": {
        {{Ticker}}: {
            "exposure": "low|medium|high" reflects how affected the company is by the bill
            "action": "buy|sell" only if exposure is high
            "reason": "" one or two sentences (only if exposure is high)
        }
    },
    "summary": ""
}
"""

countries = [i[0] for i in db.get_countries()]
sectors = [i[0] for i in db.get_sectors()]


def agent_p(rawBill):
    response = client.converse(
        modelId = "openai.gpt-oss-120b-1:0",
        messages = [
            {
                "role": "user",
                "content": [{"text": agent_p_prompt}]
            },
            {
                "role": "user",
                "content": [{"text": rawBill}]
            }
        ],
        inferenceConfig={
            "temperature": 0.05,
        }
    )
    return response["output"]["message"]["content"][1]["text"]


def agent_a(agent_p_res, compInfo):
    response = client.converse(
        modelId = "openai.gpt-oss-120b-1:0",
        messages = [
            {
                "role": "user",
                "content": [{"text": agent_a_prompt}]
            },
            {
                "role": "user",
                "content": [{"text": f"""Inputs:
                Bill: {agent_p_res}

                Companies information:
                {compInfo}"""}]
            }
        ],
        inferenceConfig={
            "temperature": 0.01
        }
    )
    return response["output"]["message"]["content"][1]["text"]


def agent_u(agent_p_res, agent_a_res):
    response = client.converse(
        modelId = "openai.gpt-oss-120b-1:0",
        messages = [
            {
                "role": "user",
                "content": [{"text": agent_u_prompt}]
            },
            {
                "role": "user",
                "content": [{"text": f"""Inputs:
                Bill: {agent_p_res}

                Companies information:
                {agent_a_res}"""}]
            }
        ],
        inferenceConfig={
            "temperature": 0
        }
    )
    return response["output"]["message"]["content"][1]["text"]


def agent_l(agent_p_res, agent_a_res, agent_u_res):
    response = client.converse(
        modelId = "openai.gpt-oss-120b-1:0",
        messages = [
            {
                "role": "user",
                "content": [{"text": agent_l_prompt}]
            },
            {
                "role": "user",
                "content": [{"text": f"""Inputs:
                Bill: {agent_p_res}

                Companies information:
                {agent_a_res}
                Impact on suppliers/clients (may not be provided for each company):
                {agent_u_res}"""}]
            }
        ],
        inferenceConfig={
            "temperature": 0
        }
    )
    return response["output"]["message"]["content"][1]["text"]
