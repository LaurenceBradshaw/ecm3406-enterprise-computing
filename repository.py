import os
import requests

FIREBASE_DB = os.environ["FIREBASE_DB"]
FIREBASE_URL = f"https://{FIREBASE_DB}-default-rtdb.europe-west1.firebasedatabase.app/" 

class Repository:
    def __init__(self,table):
        self.table = table 
  
    def clear(self):
        url = f"{FIREBASE_URL}/{self.table}.json"

        try:
            response = requests.delete(url, timeout=5)
        except requests.RequestException:
            return False
        
        if not (200 <= response.status_code < 300):
            return False

        return True

    def insert(self, js):
        url = f"{FIREBASE_URL}/{self.table}/{js['id']}.json"

        data = {
            "regx": js["regx"],
            "sub": js["sub"]
        }

        try:
            response = requests.put(url, json=data)
        except requests.RequestException:
            return False

        if not (200 <= response.status_code < 300):
            return False

        return True

    def update(self,js):
        url = f"{FIREBASE_URL}/{self.table}/{js['id']}.json"

        data = {
            "regx": js["regx"],
            "sub": js["sub"]
        }

        try:
            response = requests.patch(url, json=data, timeout=5)
        except requests.RequestException:
            return False
        
        if not (200 <= response.status_code < 300):
            return False
        
        return True

    def lookup(self, id):
        url = f"{FIREBASE_URL}/{self.table}/{id}.json"

        try:
            response = requests.get(url)
        except requests.RequestException:
            return None
    
        if not (200 <= response.status_code < 300):
            return None

        data = response.json()

        if data is None:
            return None

        return {
            "id": id,
            "regx": data.get("regx"),
            "sub": data.get("sub")
        }

    def delete(self, id):
        url = f"{FIREBASE_URL}/{self.table}/{id}.json"

        try:
            response = requests.delete(url, timeout=5)
        except requests.RequestException:
            return False

        if not (200 <= response.status_code < 300):
            return False

        return True

    def get_ids(self):
        url = f"{FIREBASE_URL}/{self.table}.json"

        try:
            response = requests.get(url, timeout=5)
        except requests.RequestException:
            return None

        if not (200 <= response.status_code < 300):
            return None

        data = response.json()
        if data is None:
            return []

        return list(data.keys())