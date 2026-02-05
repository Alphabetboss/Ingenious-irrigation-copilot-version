from roboflow import Roboflow

def load_project(api_key, workspace, project):
    rf = Roboflow(api_key=api_key)
    return rf.workspace(workspace).project(project)
