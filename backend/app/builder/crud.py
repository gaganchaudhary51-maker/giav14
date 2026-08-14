from dataclasses import dataclass,asdict

@dataclass(frozen=True)
class CrudSpec:
    entity:str
    fields:list
    roles:list
    auth:bool
    frontend:str
    backend:str
    database:str

def normalize_spec(entity,fields=None,roles=None):
    if not entity.strip(): raise ValueError("entity required")
    clean=[]
    for f in fields or ["name","created_at"]:
        if isinstance(f,str) and f.strip() and f.strip() not in clean: clean.append(f.strip())
    return CrudSpec(entity.strip(),clean,roles or ["admin","user"],True,"react-typescript","fastapi","mongodb")

def generate_manifest(spec:CrudSpec):
    e=spec.entity.lower().replace(" ","_")
    return {
      "template":"authenticated-crud-saas","entity":spec.entity,
      "files":[f"frontend/src/pages/{e}/List.tsx",f"frontend/src/pages/{e}/Form.tsx",
               f"backend/app/api/{e}.py",f"backend/app/models/{e}.py",
               f"backend/app/services/{e}.py",f"backend/tests/test_{e}.py"],
      "database":{"collection":e,"fields":spec.fields,"migration":"SAFE_SCHEMA_UPDATE"},
      "security":{"authentication":spec.auth,"roles":spec.roles},
      "status":"SPEC_GENERATED_NOT_EXECUTED"
    }
