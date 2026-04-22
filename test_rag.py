import os
import requests
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("OPENWEBUI_BASE_URL", "http://localhost:3000") + "/api/v1/knowledge"
headers = {"Authorization": f"Bearer " + os.getenv("OPENWEBUI_API_KEY")}

resp = requests.get(url, headers=headers)
print("KBs:", [k["id"] for k in resp.json()])
kb_id = resp.json()[0]["id"]

kb_resp = requests.get(f"{url}/{kb_id}", headers=headers)
print("KB Details:", kb_resp.json())

# Check how to get file contents
if "files" in kb_resp.json():
    files = kb_resp.json()["files"]
    print("Files:", files)
    if len(files) > 0:
        f_id = files[0]["id"]
        f_url = os.getenv("OPENWEBUI_BASE_URL", "http://localhost:3000") + f"/api/v1/files/{f_id}/content"
        f_resp = requests.get(f_url, headers=headers)
        print("File content snippet:", f_resp.text[:200])
