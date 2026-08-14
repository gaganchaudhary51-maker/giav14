import re
def _name(entity):
    return re.sub(r"[^a-z0-9_]+","_",entity.lower().strip()).strip("_") or "item"
def _class(entity):
    return "".join(x.capitalize() for x in re.split(r"[^a-zA-Z0-9]+",entity) if x) or "Item"
def generate_files(entity, fields, roles):
    n=_name(entity); c=_class(entity)
    py_fields="\n".join(["    %s: str | None = None" % f for f in fields]) or "    pass"
    ts_fields="\n".join(["  %s?: string;" % f for f in fields])
    backend = '''from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
router=APIRouter(prefix="/api/{n}",tags=["{n}"])
class {c}In(BaseModel):
{py_fields}
_store={{}}
@router.get("")
def list_{n}(): return list(_store.values())
@router.post("")
def create_{n}(payload:{c}In):
    item=payload.model_dump(); item["id"]=str(len(_store)+1); _store[item["id"]]=item; return item
@router.get("/{{item_id}}")
def get_{n}(item_id:str):
    if item_id not in _store: raise HTTPException(404,"Not found")
    return _store[item_id]
@router.put("/{{item_id}}")
def update_{n}(item_id:str,payload:{c}In):
    if item_id not in _store: raise HTTPException(404,"Not found")
    _store[item_id].update(payload.model_dump()); return _store[item_id]
@router.delete("/{{item_id}}")
def delete_{n}(item_id:str):
    if item_id not in _store: raise HTTPException(404,"Not found")
    return _store.pop(item_id)
'''.format(n=n,c=c,py_fields=py_fields)
    frontend = '''import React from "react";
export type {c} = {{ id:string;
{ts_fields}
}};
export default function {c}List() {{
  return <section><h1>{entity}</h1><p>Authenticated CRUD resource: {n}</p></section>;
}}
'''.format(c=c,ts_fields=ts_fields,entity=entity,n=n)
    files={}
    files["frontend/src/pages/%s/List.tsx"%n]=frontend
    files["frontend/src/pages/%s/Form.tsx"%n]=frontend.replace(c+"List",c+"Form")
    files["backend/app/api/%s.py"%n]=backend
    files["backend/tests/test_%s.py"%n]="def test_%s_contract():\\n    assert %r\\n    assert %r\\n"%(n,fields,roles)
    files["backend/app/models/%s.py"%n]="COLLECTION = %r\\nFIELDS = %r\\nROLES = %r\\n"%(n,fields,roles)
    files["backend/app/services/%s.py"%n]="ENTITY = %r\\n"%entity
    return files
