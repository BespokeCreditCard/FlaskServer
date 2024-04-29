from dotenv import load_dotenv
import os 
import re

load_dotenv()

def for_mysql():
    pattern = r"jdbc:mysql://([\w.-]+):(\d+)/(\w+)\?serverTimezone=UTC"
    match = re.match(pattern, os.environ.get("DBURL"))
    host = match.group(1)
    port = match.group(2)
    db = match.group(3)
    user = os.environ.get("DBID")
    pw = os.environ.get("DBPW")
    return host, port, user, pw, db

def dall_e_info():
    dalle_api_key = os.environ.get("DALLE")
    return dalle_api_key