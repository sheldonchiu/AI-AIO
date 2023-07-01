import logging
from gradient import NotebooksClient
from gradient import MachineTypesClient
from gradient import ProjectsClient

logger = logging.getLogger(__name__)

notebook_base_url = "https://{}.{}.paperspacegradient.com?token={}"
class Paperspace_client():
    def __init__(self, api_key):
        self.api_key = api_key
        self.notebooks_client = NotebooksClient(api_key)
        self.machineTypes_client = MachineTypesClient(api_key)
        self.projects_client = ProjectsClient(api_key)
        
    def find_available_gpu(self, priority) -> str:
        VMs = [vm.label for vm in self.machineTypes_client.list()]
        for p in priority:
            if p in VMs:
                return p
        return None
    
    def create_project(self, name):
        project_list = self.projects_client.list()
        for p in project_list:
            if p.name == name:
                return p.id
        return self.projects_client.create(name=name)

    def list_available_gpu(self):
        return [vm.label for vm in self.machineTypes_client.list()]

    def get_notebook_detail(self, notebook_id):
        return self.notebooks_client.get(id=notebook_id)
    
    def delete_notebook_in_project(self, project_id):
        notebooks = self.get_notobooks_by_project_id(project_id)
        for n in notebooks:
            self.notebooks_client.delete(id=n.id)

    def get_notobooks_by_project_id(self, project_id):
        notebooks = [n for n in self.notebooks_client.list(tags=[]) if n.project_handle==project_id]
        return notebooks

    def get_notobooks_by_project_name(self, project_name):
        project_list = self.projects_client.list()
        for project in project_list:
            if project.name == project_name:
                project_id = project.id
                break
        notebooks = [n for n in self.notebooks_client.list(tags=[]) if n.project_handle==project_id]
        return notebooks
    
    def create_notebook(self, **kwargs):
        return self.notebooks_client.create(**kwargs)
    
    def start_notebook(self, notebook_id, machine_type):
        return self.notebooks_client.start(id=notebook_id, 
                                           machine_type=machine_type,
                                           shutdown_timeout='6')
        
    def get_notebook_url(self, notebook_status):
        return notebook_base_url.format(notebook_status.id, notebook_status.cluster_id, notebook_status.token)
