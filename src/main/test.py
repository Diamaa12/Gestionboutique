import os
import pathlib
from pprint import pprint
import json


script_path = os.path.join(os.path.dirname(__file__), "resources", "postgres_installateur",
                               "install_postgresql.bat")
print(script_path)
p = os.path.join(os.path.dirname(__file__), "resources", "database", "gestion_boutique.sql")
print(p)
path = pathlib.Path.cwd()
print(path)
with open(os.path.join(os.path.dirname(__file__), "resources", "database", "test.json"), "r") as f:
    sql_script = f.read()
print(sql_script)
pat = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
print(pat)