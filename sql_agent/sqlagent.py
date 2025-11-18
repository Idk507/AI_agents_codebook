import re
import pathlib
import requests
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_community.utilities import SQLDatabase 
from langchain_core.messages import SystemMessage 
from langchain_core.tools import tool 

llm = init_chat_model("openai:gpt-4")

#get the database ,store it locally

url = "https://storage.googleapis.com/benchmarks-artifacts/chinook/Chinook.db"
local_path = pathlib.Path("Chinook.db")

if local_path.exits():
  print(f"{local_path} alreay exists")
else:
  response = requests.get(url)
  if response.status_code == 200 :
    local_path.write_bytes(response.content)
  else :
    print(f"Failed to download {response.status})

db = SQLDatabase.from_uri("sqlite://chinook.db")


SCHEMA = db.get_table_info()

DENY_RE = re.compile(
    r"\b(INSERT|UPDATE|DELETE|ALTER|DROP|CREATE|REPLACE|TRUNCATE)\b", re.I
)
HAS_LIMIT_TAIL_RE = re.compile(r"(?is)\blimit\b\s+\d+(\s*,\s*\d+)?\s*;?\s*$")


def _safe_sql(q : str ):
    q = q.strip()
    if q.count(";") > 1 or (q.endswith(";") and ";" in q[:-1]):
        return "Error multiple statement are not allowed"
    q = q.rstrip(";").strip()
    if not q.lower().startswith("select"):
        return "Error : only select statmeents are allowed"
    if DENY_RE.search(q):
        return "Error : DML?DD: detected.only real only query are permitted"

    if not HAS_LIMIT_TAIL_RE.search(q):
        q+= " LIMIT 5 "
    return q


@tool 
def execute_sql(query : str) -> str:
    query = _safe_sql(query)
    q = query 
    if q.startswith("Error:"):
        return q
    try :
      return db.run(q)
    except Exception as e :
      return f"Error : {e}"

SYSTEM_PROMPT = f"""You are a careful SQLite analyst.

Authoritative schema (do not invent columns/tables):
{SCHEMA}

Rules:
- Think step-by-step.
- When you need data, call the tool `execute_sql` with ONE SELECT query.
- Read-only only; no INSERT/UPDATE/DELETE/ALTER/DROP/CREATE/REPLACE/TRUNCATE.
- Limit to 5 rows unless user explicitly asks otherwise.
- If the tool returns 'Error:', revise the SQL and try again.
- Limit the number of attempts to 5. 
- If you are not successful after 5 attempts, return a note to the user.
- Prefer explicit column lists; avoid SELECT *.
"""


agent = create_agent( model = llm ,tools = [execute_sql],system_prompt = SYSTEM_PROMPT)
