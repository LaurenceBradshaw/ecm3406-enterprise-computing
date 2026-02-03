import os
from typing import Any
import requests
from requests.status_codes import codes

FIREBASE_DB = os.environ["FIREBASE_DB"]
FIREBASE_URL = f"https://{FIREBASE_DB}-default-rtdb.europe-west1.firebasedatabase.app/" 

# All IDs are internally prefixed with an underscore to avoid issues with Firebase treatings numeric keys with array semantics.
# This underscore shouldn't leak outside this repository layer.

class Repository:
    """
    Repository class to interact with Firebase Realtime Database for guardrail storage.
    """
    def __init__(self,table):
        self.table = table 
  
    def clear(self) -> None | bool:
        """
        Clear all entries in the specified table.
        
        :return: None on error, True on success, False on failure
        :rtype: None | bool
        """
        url = f"{FIREBASE_URL}/{self.table}.json"

        try:
            response = requests.delete(url)
        except requests.RequestException:
            return None
        
        if not (200 <= response.status_code < 300):
            return False

        return True

    def insert(self, js: dict[str, Any]) -> None | bool:
        """
        Insert a new entry into the specified table.
        
        :param js: JSON object representing the entry to insert
        :type js: dict[str, Any]
        :return: None on error, True on success, False on failure
        :rtype: None | bool
        """
        url = f"{FIREBASE_URL}/{self.table}/_{js['id']}.json"

        data = {
            "regx": js["regx"],
            "sub": js["sub"]
        }

        try:
            response = requests.put(url, json=data)
        except requests.RequestException:
            return None

        if not (200 <= response.status_code < 300):
            return False

        return True

    def update(self, js: dict[str, Any]) -> None | bool:
        """
        Update an existing entry in the specified table.
        
        :param js: JSON object representing the entry to update
        :type js: dict[str, Any]
        :return: None on error, True on success, False on failure
        :rtype: bool | None
        """
        url = f"{FIREBASE_URL}/{self.table}/_{js['id']}.json"

        data = {
            "regx": js["regx"],
            "sub": js["sub"]
        }

        try:
            response = requests.patch(url, json=data)
        except requests.RequestException:
            return None
        
        if not (200 <= response.status_code < 300):
            return False
        
        return True

    def lookup(self, id: str) -> None | bool | dict[str, Any]:
        """
        Lookup an entry by its ID in the specified table.
        
        :param id: ID of the entry to lookup
        :type id: str
        :return: None on error, False on failure, or dict with entry data on success
        :rtype: bool | dict[str, Any] | None
        """
        url = f"{FIREBASE_URL}/{self.table}/_{id}.json"

        try:
            response = requests.get(url)
        except requests.RequestException:
            return None
    
        if not (200 <= response.status_code < 300):
            return False
        
        data = response.json()
        if data is None:
            return {}

        return {
            "id": id,
            "regx": data.get("regx"),
            "sub": data.get("sub")
        }

    def delete(self, id: str) -> None | bool:
        """
        Delete an entry by its ID in the specified table.
        
        :param id: ID of the entry to delete
        :type id: str
        :return: None on error, True on success, False on failure
        :rtype: bool | None
        """
        url = f"{FIREBASE_URL}/{self.table}/_{id}.json"

        try:
            response = requests.delete(url)
        except requests.RequestException:
            return None

        if not (200 <= response.status_code < 300):
            return False

        return True

    def get_ids(self) -> None | bool | list[str]:
        """
        Get a list of all entry IDs in the specified table.
        
        :return: None on error, False on failure, or list of IDs on success
        :rtype: bool | list[str] | None
        """
        url = f"{FIREBASE_URL}/{self.table}.json"

        try:
            response = requests.get(url)
        except requests.RequestException:
            return None

        if not (200 <= response.status_code < 300):
            return False

        data = response.json()
        if data is None:
            return []
        
        return [key[1:] for key in data.keys()]