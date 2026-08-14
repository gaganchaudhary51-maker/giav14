from app.collaboration.bus import collaboration_bus

SYSTEM_ACTORS={
 "gia":"commander",
 "gini":"copilot",
 "agent":"worker"
}

def send(sender,recipient,content,task_id=None,message_type="TASK"):
    if sender not in SYSTEM_ACTORS and not sender.startswith("agent:"):
        raise ValueError("Unknown sender")
    if recipient not in SYSTEM_ACTORS and recipient!="*" and not recipient.startswith("agent:"):
        raise ValueError("Unknown recipient")
    return collaboration_bus.send(sender,recipient,message_type,content,task_id)

def handoff(sender,recipient,task_id,summary):
    return send(sender,recipient,summary,task_id,"HANDOFF")

def result(sender,recipient,task_id,evidence):
    return send(sender,recipient,evidence,task_id,"RESULT")

def approval_request(sender,recipient,task_id,risk):
    return send(sender,recipient,risk,task_id,"APPROVAL_REQUIRED")
