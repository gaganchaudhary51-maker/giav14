from app.learning.engine import learning_engine
def learn_from_result(agent,domain,lesson,evidence,tests_passed):return learning_engine.add(agent,domain,lesson,evidence,tests_passed)
def self_update_policy():
    return {"mode":"evidence-gated","automatic_code_write":False,"requires_tests":True,
            "rules":["No untested lesson may be promoted","No automatic source-code self-modification",
                     "Promoted lessons remain project-scoped through retrieval","Rollback requires checkpointed artifacts"],
            "status":"ENABLED"}
