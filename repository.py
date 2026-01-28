import os
import requests
from requests.status_codes import codes

FIREBASE_DB = os.environ["FIREBASE_DB"]
FIREBASE_URL = f"https://{FIREBASE_DB}-default-rtdb.europe-west1.firebasedatabase.app/" 

# All IDs are internally prefixed with an underscore to avoid issues with Firebase treatings numeric keys with array semantics.
# This underscore shouldn't leak outside this repository layer.

class Repository:
    def __init__(self,table):
        self.table = table 
  
    def clear(self):
        url = f"{FIREBASE_URL}/{self.table}.json"

        try:
            response = requests.delete(url)
        except requests.RequestException:
            return {}, codes.internal_server_error
        
        if not (200 <= response.status_code < 300):
            return {}, codes.internal_server_error

        return {}, codes.no_content

    def insert(self, js):
        url = f"{FIREBASE_URL}/{self.table}/_{js['id']}.json"

        data = {
            "regx": js["regx"],
            "sub": js["sub"]
        }

        try:
            response = requests.put(url, json=data)
        except requests.RequestException:
            return {}, codes.internal_server_error

        if not (200 <= response.status_code < 300):
            return {}, codes.internal_server_error

        return {}, codes.created

    def update(self,js):
        url = f"{FIREBASE_URL}/{self.table}/_{js['id']}.json"

        data = {
            "regx": js["regx"],
            "sub": js["sub"]
        }

        try:
            response = requests.patch(url, json=data)
        except requests.RequestException:
            return {}, codes.internal_server_error
        
        if not (200 <= response.status_code < 300):
            return {}, codes.internal_server_error
        
        return {}, codes.no_content

    def lookup(self, id):
        url = f"{FIREBASE_URL}/{self.table}/_{id}.json"

        try:
            response = requests.get(url)
        except requests.RequestException:
            return {}, codes.internal_server_error
    
        if not (200 <= response.status_code < 300):
            return {}, codes.internal_server_error
        
        data = response.json()
        if data is None:
            return {}, codes.not_found

        return {
            "id": id,
            "regx": data.get("regx"),
            "sub": data.get("sub")
        }, codes.ok

    def delete(self, id):
        url = f"{FIREBASE_URL}/{self.table}/_{id}.json"

        try:
            response = requests.delete(url)
        except requests.RequestException:
            return {}, codes.internal_server_error

        if not (200 <= response.status_code < 300):
            return {}, codes.internal_server_error

        return {}, codes.no_content

    def get_ids(self):
        url = f"{FIREBASE_URL}/{self.table}.json"

        try:
            response = requests.get(url)
        except requests.RequestException:
            return [], codes.internal_server_error

        if not (200 <= response.status_code < 300):
            return [], codes.internal_server_error

        data = response.json()
        if data is None:
            return [], codes.ok
        
        return [key[1:] for key in data.keys()], codes.ok