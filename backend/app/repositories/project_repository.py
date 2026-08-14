from app.db.store import ProjectStore

store = ProjectStore()

def list_projects():
    return store.list()

def create_project(project):
    return store.create(project)
