###############################################################
## test5.py                                                  ## 
###############################################################
import requests
import unittest
import database

LLM = "http://localhost:3000/llm"
GUARDRAILS = "http://localhost:3001/guardrails"
AUBERGE = "http://localhost:3002/auberge"

class Testing(unittest.TestCase):
  ############################################################
  ## test_001_llm				            ##
  ############################################################
  def test_001_llm(self):
    js  = {"prompt":"What is the melting point of silver?"}
    rsp = requests.post(LLM,json=js)

    self.assertEqual(rsp.status_code,200)
    self.assertTrue("961" in rsp.json()["output"])

  ############################################################
  ## test_002_guardrails				    ##
  ############################################################
  def test_002_guardrails(self):
    database.db.clear()

    id   = "931"
    regx = r"Prince Andrew"
    sub  = "Andrew Mountbatten-Windsor"
    js   = {"id":id,"regx":regx,"sub":sub}

    rsp = requests.put(f'{GUARDRAILS}/{id}',json=js)
    self.assertEqual(rsp.status_code,201)

    rsp = requests.get(f'{GUARDRAILS}/{id}')
    self.assertEqual(rsp.status_code,200)
    self.assertEqual(id,rsp.json()["id"])
    self.assertEqual(regx,rsp.json()["regx"])
    self.assertEqual(sub,rsp.json()["sub"])

  ############################################################
  ## test_003_guardrails				    ##
  ############################################################
  def test_003_guardrails(self):
    database.db.clear()

    id   = "email-001"
    regx = r"[a-zA-Z0-9_.]+@[a-zA-Z0-9-]+.[a-zA-Z0-9-.]+" 
    sub  = "<Email address>"
    js   = {"id":id,"regx":regx,"sub":sub}

    rsp = requests.put(f'{GUARDRAILS}/{id}',json=js)
    self.assertEqual(rsp.status_code,201)

    rsp = requests.get(f'{GUARDRAILS}/{id}')
    self.assertEqual(rsp.status_code,200)
    self.assertEqual(id,rsp.json()["id"])
    self.assertEqual(regx,rsp.json()["regx"])
    self.assertEqual(sub,rsp.json()["sub"])

  ############################################################
  ## test_004_guardrails				    ##
  ############################################################
  def test_004_guardrails(self):
    database.db.clear()

    id   = "Broken"
    regx = r"*a-z]" 
    sub  = "anything"
    js   = {"id":id,"regx":regx,"sub":sub}

    rsp = requests.put(f'{GUARDRAILS}/{id}',json=js)
    self.assertEqual(rsp.status_code,400) # Bad input

  ############################################################
  ## test_005_guardrails_put_is_idempotent                 ##
  ############################################################
  def test_005_guardrails_put_is_idempotent(self):
      database.db.clear()

      id   = "dup-001"
      regx = r"abc"
      sub  = "first"
      js   = {"id": id, "regx": regx, "sub": sub}

      rsp = requests.put(f'{GUARDRAILS}/{id}', json=js)
      self.assertEqual(rsp.status_code, 201)

      js2 = {"id": id, "regx": r"def", "sub": "second"}
      rsp = requests.put(f'{GUARDRAILS}/{id}', json=js2)
      self.assertEqual(rsp.status_code, 204)

      rsp = requests.get(f'{GUARDRAILS}/{id}')
      self.assertEqual(rsp.json()["regx"], "def")
      self.assertEqual(rsp.json()["sub"], "second")

  ############################################################
  ## test_006_guardrails_id_mismatch                      ##
  ############################################################
  def test_006_guardrails_id_mismatch(self):
      database.db.clear()

      js = {"id": "x", "regx": r"abc", "sub": "y"}
      rsp = requests.put(f'{GUARDRAILS}/z', json=js)

      self.assertEqual(rsp.status_code, 400)

  ############################################################
  ## test_007_guardrails_missing_field                   ##
  ############################################################
  def test_007_guardrails_missing_field(self):
      database.db.clear()

      js = {"id": "missing", "regx": r"abc"}
      rsp = requests.put(f'{GUARDRAILS}/missing', json=js)

      self.assertEqual(rsp.status_code, 400)

  ############################################################
  ## test_008_guardrails_invalid_json                    ##
  ############################################################
  def test_008_guardrails_invalid_json(self):
      database.db.clear()

      rsp = requests.put(
          f'{GUARDRAILS}/bad',
          data="not json",
          headers={"Content-Type": "application/json"}
      )

      self.assertEqual(rsp.status_code, 400)

  ############################################################
  ## test_009_guardrails_get_missing                     ##
  ############################################################
  def test_009_guardrails_get_missing(self):
      database.db.clear()

      rsp = requests.get(f'{GUARDRAILS}/nope')
      self.assertEqual(rsp.status_code, 404)

  ############################################################
  ## test_010_guardrails_delete                          ##
  ############################################################
  def test_010_guardrails_delete(self):
      database.db.clear()

      js = {"id": "del-001", "regx": r"abc", "sub": "x"}
      requests.put(f'{GUARDRAILS}/del-001', json=js)

      rsp = requests.delete(f'{GUARDRAILS}/del-001')
      self.assertEqual(rsp.status_code, 204)

      rsp = requests.get(f'{GUARDRAILS}/del-001')
      self.assertEqual(rsp.status_code, 404)

  ############################################################
  ## test_013_guardrails_list_empty                      ##
  ############################################################
  def test_013_guardrails_list_empty(self):
      database.db.clear()

      rsp = requests.get(f'{GUARDRAILS}')
      self.assertEqual(rsp.status_code, 200)
      self.assertEqual(rsp.json(), [])

  ############################################################
  ## test_014_guardrails_list_non_empty                 ##
  ############################################################
  def test_014_guardrails_list_non_empty(self):
      database.db.clear()

      js1 = {"id": "1", "regx": r"abc", "sub": "x"}
      js2 = {"id": "2", "regx": r"def", "sub": "y"}

      requests.put(f'{GUARDRAILS}/1', json=js1)
      requests.put(f'{GUARDRAILS}/2', json=js2)

      rsp = requests.get(f'{GUARDRAILS}')
      self.assertEqual(rsp.status_code, 200)

      ids = rsp.json()
      self.assertEqual(type(ids), list)
      self.assertEqual(set(ids), {"1", "2"})

  ############################################################
  ## test_015_delete_resource_doesnt_exist                  ##
  ############################################################
  def test_015_delete_resource_doesnt_exist(self):
      database.db.clear()

      rsp = requests.delete(f'{GUARDRAILS}/nonexistent')
      self.assertEqual(rsp.status_code, 404)

  ############################################################
  ## test_005_auberge                                       ##
  ############################################################
  def test_005_auberge(self):
    database.db.clear()

    id   = "Roma"
    regx = r"Rome" 
    sub  = "Roma"
    js   = {"id":id,"regx":regx,"sub":sub}

    rsp = requests.put(f'{GUARDRAILS}/{id}',json=js)
    self.assertEqual(rsp.status_code,201) # Created 

    id2   = "Firenze"
    regx2 = r"Florence" 
    sub2  = "Firenze"
    js2   = {"id":id2,"regx":regx2,"sub":sub2}

    rsp = requests.put(f'{GUARDRAILS}/{id2}',json=js2)
    self.assertEqual(rsp.status_code,201) # Created 

    js3 = {"prompt":"What are the major cities of Italy?"}
    rsp = requests.post(AUBERGE,json=js3)
    self.assertEqual(rsp.status_code,200)
    self.assertTrue("Roma" in rsp.json()["output"])
    self.assertTrue("Firenze" in rsp.json()["output"])
