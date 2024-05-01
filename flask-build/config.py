from dotenv import load_dotenv
import os 
import re

load_dotenv()

DEEPL = os.environ.get("DEEPL")
DALLE_API_KEY = os.environ.get("DALLE")
pattern = r"jdbc:mysql://([\w.-]+):(\d+)/(\w+)\?serverTimezone=UTC"
match = re.match(pattern, os.environ.get("DBURL"))
HOST = match.group(1)
PORT = match.group(2)
DB = match.group(3)
USER = os.environ.get("DBID")
PW = os.environ.get("DBPW")
def for_mysql() :
    return HOST, str(PORT), USER, PW, DB
