from app.utils.constants import *
from app.utils.functions import *
import pynecone as pc
from pynecone.utils import types
from app.app import BaseState
from pynecone.event import EventHandler
from typing import Optional, Dict, List, Union, Set
import typing
from sqlmodel import Field, select
from app.backend.paperspace_util import Paperspace_client
import asyncio
import time
import json
from collections import OrderedDict
from pynecone import constants

import logging
logger = logging.getLogger(__name__)

class Environment(pc.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    env_name: str
    env_api_key: str
    env_project_id: Optional[str]
    env_notebook_id: Optional[str]

    env_workspace: Optional[str]
    env_auto_timeout: Optional[str]
    
    env_workspace_ref: Optional[str]
    env_workspace_username: Optional[str]
    env_workspace_password: Optional[str]
    
    env_container: Optional[str]
    env_registry_username: Optional[str]
    env_registry_password: Optional[str]
    
    env_command: Optional[str] 
    
    env_type: str
    extra_info: Optional[str]

class PaperspaceState(BaseState):
    """Represents the state of the Paperspace app.

    Attributes:
        power_light (str): The color of the power light, either "red-700" or "green-700".
        power_button (str): The label of the power button, either "Start" or "Stop".
        show_progress_for_start_button (bool): Whether to show progress when the "Start" button is clicked.
        environments (List[Environment]): A list of available environments.
        env_type (str): The type of the currently selected environment.
        retry_count (int): The number of times a retry has been attempted.
        retry_str (str): A string describing what is being retried.
        interrupt_running (bool): A signal to interrupt the current start job.

    Properties:
        display_retry_count (bool): Whether the retry count is greater than zero.
        retry_count_str (str): A string representation of the retry count and retry string.
        is_env_selected (bool): Whether an environment has been selected.

    Methods:
        update_envs(): Updates the list of available environments.
        _toggle_power(status): Toggles the power button and light based on the given status.
    """
    power_light: str = "red-700"
    power_button: str = "Start"
    show_progress_for_start_button: bool = False
    environments: List[Environment] = []
    env_type: str = ""
    retry_count: int = 0
    retry_str = ""
    _task_to_interrupt: Set[str] = set()
    _task_need_wait: Set[str] = set()
    _background_tasks: Set[str] = set()

    @pc.var
    def display_retry_count(self) -> bool:
        return self.retry_count > 0
    
    @pc.var
    def retry_count_str(self) -> str:
        return f"{self.retry_str}: {self.retry_count}"

    @pc.var
    def is_env_selected(self) -> bool:
        return self.env_type != ""
    
    @pc.var
    def get_env_download_link(self) -> str:
        return f"{constants.API_URL}/download_env/{self.get_token()}"
    
    def interrupt_task(self, name:str):
        self._task_to_interrupt.add(name)
    
    def update_envs(self):
        if WEB_HOSTING == False:
            try:
                with pc.session() as session:
                    self.environments = session.exec(select(Environment)).all()
            except:
                print_msg(self, "Error", "Failed to fetch environments from database.")

    def _toggle_power(self, status):
        if status:
            self.power_button = "Stop"
            self.power_light = "green-700"
        else:
            self.power_button = "Start"
            self.power_light = "red-700"
        
def timeout_check(start_time: float):
    """Checks if the elapsed time since the given start time has exceeded the predefined timeout.

    Args:
        start_time (float): The start time in seconds since the epoch.

    Raises:
        Exception: If the elapsed time has exceeded the Paperspace timeout limit.

    Returns:
        None
    """
    if time.time() - start_time > PAPERSPACE_TIMEOUT:
        raise Exception("Timeout")    
            
class NewEnvState(PaperspaceState):
    
    env_api_key: str = ""
    env_workspace: str = "https://github.com/sheldonchiu/Ultimate-Paperspace-Template.git"
    env_auto_timeout: str = "6"
    
    env_workspace_ref: str = ""
    env_workspace_username: str = ""
    env_workspace_password: str = ""
    
    env_container: str = PAPERSPACE_DEFAULT_CONTAINER
    env_registry_username: str = ""
    env_registry_password: str = ""
    
    env_command: str = PAPERSPACE_DEFAULT_COMMAND
    
    _new_env_required_env_vars: List[str] = ["env_name", "env_api_key", "env_container", "env_workspace", "env_auto_timeout", "env_command"]
    
    _environment_variables: Dict[str, str] = {}
    
    def _add_script(self, script):
        if self._environment_variables.get('RUN_SCRIPT', None) is None:
            self._environment_variables['RUN_SCRIPT'] = script
        else:
            self._environment_variables['RUN_SCRIPT'] += f",{script}"
        
from .paperspace_extra import ToolState    
class EnvState(ToolState):
    
    env_id: str # int will cause issue with select
    env_name: str = ""
    env_project_id: str = ""
    env_notebook_id: str = ""
    
    notebook_url: str = ""
    
    _existing_env_required_env_vars: List[str] = ["env_name", "env_api_key", "env_project_id", "env_notebook_id"]
    
    gpu_list: typing.OrderedDict[str,bool] = OrderedDict({
        gpu:False for gpu in ALL_GPU
    })
    gpu_available: Dict[str,str] = {
        gpu: "text-green-500" for gpu in ALL_GPU
    }
    free_gpu: bool = False
    pro_gpu: bool = False
    growth_gpu: bool = False
    
    _client: Optional[Paperspace_client] = None
    _gpu_priority: List[str] = []
    _start_time: float = 0
    
    def _clean_exit_task(self, name):
        self._task_to_interrupt.discard(name)
        self._background_tasks.discard(name)
        self._task_need_wait.discard(name)
    
    def _reset_env(self, all=False):
        defaults = EnvState.get_fields()
        for key in self.vars.keys():
            if key.startswith("env_") or key.startswith('extra_') and (all or key != 'env_type'):
                if key == "env_api_key":
                    continue
                elif key in defaults:
                    try:
                        if types._issubclass(type(defaults[key].default), Dict):
                            target = getattr(self, key)
                            for k in defaults[key].default.keys():
                                target[k] = defaults[key].default[k]
                        else:
                            setattr(self, key, defaults[key].default)  
                    except:
                        logger.exception(f"Failed to reset {key}")
                    
    def _prepare_env(self, add=False):
        # Update this when adding new components
        self._environment_variables = {}
        if not add:
            self._add_command(self)
            self._add_discord(self)
        self._add_cloudflared(self,add)
        self._add_image_browser(self,add)
        self._add_sd_webui(self,add)
        self._add_sd_volta(self, add)
        self._add_fastchat(self,add)
        self._add_textgen(self, add)
        self._add_minio(self,add)
        self._add_rclone(self,add)
        # Start tunnel for all the components if using quick tunnel
        if self._environment_variables['CF_TOKEN'] == "quick":
            self._add_cloudflared(self,add)
                    
    def _validate_env(self, validate_gpu= False) -> bool:
        if validate_gpu and not any(self.gpu_list.values()):
            print_msg(self, "Error", "No GPU selected")
            return False
        if self.env_type == 'existing':
            required_var = self._existing_env_required_env_vars
        elif self.env_type == 'new':
             required_var = self._new_env_required_env_vars
        else:
            print_msg(self, "Error", "No environment selected")
            return False
        
        # default value will cause issue with non "" default value
        # defaults = EnvState.get_fields()
        # empty_var = [v for v in required_var if getattr(self, v) == defaults[v].default]
        empty_var = [v for v in required_var if getattr(self, v) == ""]
        for k in self.event_handlers.keys():
            if k.startswith("_check_env"):
                if result := getattr(self, k)(self, add=False):
                    empty_var += result
        if len(empty_var) > 0:
            msg = ""
            for v in empty_var:
                msg += f"{v} is empty\n"
            print_msg(self, "Error", msg)
            return False
        return True
    
    def set_action_status(self, name, status):
        var_name = f"{name}_action_in_progress"
        progress = f"{name}_action_progress"
        log = f"{name}_action_log"

        if getattr(self, var_name) is not None:
            if status:
                # clear previous log
                setattr(self, progress, "")
                setattr(self, log, "")
            setattr(self, var_name, status)
        else:
            print_msg(self, "Error", f"Unknown action {name}")
            
    @batch_update_state
    async def start_stop_notebook(self) -> Union[None, EventHandler]:
        self.retry_count = 0
        self._client = Paperspace_client(self.env_api_key)
        
        if self.power_button == "Stop":
            self._client.notebooks_client.stop(self.env_notebook_id)
            self._toggle_power(self, False)
            self.show_progress_for_start_button = False
            self.notebook_url = ""
            return
        
        if not self._validate_env(self, validate_gpu=True):
            self.show_progress_for_start_button = False
            return
        # do it this way to keep the gpu order, try best gpu first
        self._gpu_priority = [gpu for gpu in self.gpu_list.keys() if self.gpu_list[gpu]]
        self._start_time = time.time()
        self._background_tasks.add("start_notebook")
        return self.start_notebook
        
    async def start_notebook(self) -> Union[None, EventHandler]:
        if "start_notebook" in self._task_to_interrupt:
            self._clean_exit_task(self, "start_notebook")
            self.show_progress_for_start_button = False
            self.retry_count = 0
            return
        
        if "start_notebook" in self._task_need_wait:
            await asyncio.sleep(PAPERSPACE_START_RATE)
        
        try:
            if WEB_HOSTING:
                timeout_check(self._start_time)
            gpu = self._client.find_available_gpu(self._gpu_priority)
            # wait for gpu to be available
            if gpu is None:
                logger.info("No available GPU, retrying in 5 seconds")
                self.retry_str = "No GPU"
                self.retry_count += 1
                self._task_need_wait.add("start_notebook")
                return self.start_notebook
            try:
                if self.env_type == 'existing':
                    self.env_notebook_id = self._client.start_notebook(self.env_notebook_id, gpu)
                elif self.env_type == 'new':
                    self._prepare_env(self)
                    self.env_project_id = self._client.create_project(f"{self.env_name} From Toolbox")
                    self._client.delete_notebook_in_project(self.env_project_id)
                    kwargs = {
                        'machine_type': gpu,
                        'project_id': self.env_project_id,
                        'container': self.env_container,
                        'workspace': self.env_workspace,
                        'command': self.env_command,
                        'shutdown_timeout': self.env_auto_timeout,
                    }
                    
                    if self.env_registry_username != "":
                        kwargs['registry_username'] = self.env_registry_username
                    if self.env_registry_password != "":
                        kwargs['registry_password'] = self.env_registry_password
                    if self.env_workspace_ref != "":
                        kwargs['workspace_ref'] = self.env_workspace_ref
                    if self.env_workspace_username != "":
                        kwargs['workspace_username'] = self.env_workspace_username
                    if self.env_workspace_password != "":
                        kwargs['workspace_password'] = self.env_workspace_password
                    if self._environment_variables != "":
                        kwargs['environment'] = self._environment_variables
                        
                    self.env_notebook_id = self._client.create_notebook(**kwargs)
                    # raise Exception
                # Success, proceed to check status
                return self.check_notebook_status
            except:
                # Sometimes the GPU is not available after the first check
                logger.exception("Failed to start notebook")
                self.retry_str = "Failed to start"
                self.retry_count += 1
                self._task_need_wait.add("start_notebook")
                return self.start_notebook
        except Exception as e:
            print_msg(self, "Error", str(e))
            self._toggle_power(self, False)          
            self._clean_exit_task(self, "start_notebook")
        
    async def check_notebook_status(self) -> Union[None, EventHandler]:    
        
        if "start_notebook" in self._task_to_interrupt:
            self._clean_exit_task(self, "start_notebook")
            self.show_progress_for_start_button = False
            self.retry_count = 0
            return
        
        if "start_notebook" in self._task_need_wait:
            await asyncio.sleep(PAPERSPACE_START_RATE)
            
        notebook = self._client.get_notebook_detail(self.env_notebook_id)
        if notebook.state == "Running":
            self._toggle_power(self, True)
            if WEB_HOSTING == False and self.env_id != "":
                with pc.session() as session:
                    try:
                        row_to_edit = session.query(Environment).filter(
                                            Environment.id == self.env_id).first()
                        row_to_edit.env_notebook_id = self.env_notebook_id
                        row_to_edit.env_project_id = self.env_project_id
                        session.commit()
                    except:
                        print_msg(self, "Warning", "Failed to update project id and notebook id to database")
            # get notebook url
            self.notebook_url = self._client.get_notebook_url(notebook)
        else:
            logger.info("Notebook not running, retrying in 5 seconds")
            self.retry_str = "Waiting for Notebook to start"
            self.retry_count += 1
            self._task_need_wait.add("start_notebook")
            return self.check_notebook_status
        
        self.show_progress_for_start_button = False
        self.retry_count = 0
        self._clean_exit_task(self, "start_notebook")
        
    @pc.var
    def gpu_list_display(self) -> List[List[str]]:
        if self.free_gpu == self.pro_gpu == self.growth_gpu is False:
            return []

        target_gpu_list = []
        if self.free_gpu:
            target_gpu_list += FREE_GPU
            if self.growth_gpu:
                target_gpu_list += GROWTH_FREE_GPU
            if self.pro_gpu:
                target_gpu_list += PRO_FREE_GPU
        else:
            if self.growth_gpu:
                target_gpu_list += GROWTH_GPU
            if self.pro_gpu:
                target_gpu_list += PRO_GPU
  
        return [[gpu, self.gpu_available[gpu]] for gpu in target_gpu_list]    
    
    def sync(self):
        if self.env_api_key == "":
            print_msg(self, "Error", "Please enter API key")
            return
        client = Paperspace_client(self.env_api_key)
        try:
            available_gpu = client.list_available_gpu()
            for gpu in self.gpu_available.keys():
                if gpu in available_gpu:
                    self.gpu_available[gpu] = "text-green-500"
                else:
                    self.gpu_available[gpu] = "text-red-500"
            if self.env_project_id != "":
                try:
                    self._toggle_power(self, False)
                    for notebook in client.get_notobooks_by_project_id(self.env_project_id):             
                        if notebook.state == "Running":
                            self.notebook_url = client.get_notebook_url(notebook)
                            self._toggle_power(self, True)
                            return
                except:
                    print_msg(self, "Error", "Failed to get notebook status")
        except:
            logger.exception("Failed to sync")
            print_msg(self, "Error", "Failed to sync, please check if the API key is correct")
            
    def load_env(self, selected_id: str):
        if selected_id == "":
            self.env_type = ""
            self._reset_env(self)
            return
        
        # use loop instead of sql select to take care of imported environment
        row = None
        try:
            selected_id = int(selected_id)
        except:
            print_msg(self, "Error", "The given environment id is not valid")
            return
        
        for env in self.environments:
            if env.id == selected_id:
                row = env
                break
        if row is None:
            print_msg(self, "Error", "Internal error, unable to load environment")
            return
        self.env_type = row.env_type
        self.env_id = row.id
        try:
            for key in self.vars.keys():
                value = getattr(row, key, None)
                if value is not None:
                    if key.startswith("env_"):
                        setattr(self, key, value)
            extra_info = json.loads(row.extra_info)
            for key in extra_info.keys():
                if key in self.vars.keys():
                    if types._issubclass(type(extra_info[key]), Dict):
                        target = getattr(self, key)
                        for k in extra_info[key].keys():
                            target[k] =extra_info[key][k]
                    else:
                        setattr(self, key, extra_info[key])     
        except:
            print_msg(self, "Error", "Internal error, unable to load selected environment")
            return  
    
    @batch_update_state
    def save_env(self):
        if not self._validate_env(self):
            return
        
        def create_env():
            kwargs = {  key: getattr(self, key) 
                for key in self.vars.keys() 
                if key.startswith("env_") 
                and key not in  ["env_id"]
            }
            kwargs["extra_info"] = json.dumps({key: getattr(self, key) 
                                            for key in self.vars.keys() 
                                            if key.startswith("extra_")
                                        })
            return Environment(**kwargs)
        try:
            if WEB_HOSTING:
                data = create_env()
                if self.env_id != "":
                    # if env is selected, perfrom update
                    for idx, env in enumerate(self.environments):
                        if env.id == int(self.env_id):
                            data.id = env.id
                            self.environments[idx] = data
                            break
                else:
                    test_id = 0
                    used_id = [i.id for i in self.environments]
                    while True:
                        if test_id not in used_id:
                            data.id = test_id
                            self.env_id = str(data.id)
                            break
                        test_id += 1
                    self.environments.append(data)
            else:
                with pc.session() as session:
                    # if env is selected, perfrom update
                    row_to_edit = session.query(Environment).filter(
                        Environment.id == self.env_id).first()
                    if self.env_id != "" and row_to_edit is not None:
                        extra_info = {}
                        for key in self.vars.keys():
                            value = getattr(self, key, None)
                            if value is not None:
                                if key.startswith("env_") and key != "env_id":
                                    setattr(row_to_edit, key, value)
                                elif key.startswith("extra_"):
                                    extra_info[key] = value
                        row_to_edit.extra_info = json.dumps(extra_info)
                        session.commit()
                    # if env is not selected, perform insert
                    else:
                        data = create_env()
                        session.add(data)
                        session.commit()
                        self.env_id = str(data.id)
                        
                    self.update_envs.fn(self)
        except:
            print_msg(self, "Error", "Internal error, unable to save environment")
            return

        print_msg(self, "Success", "Environment saved.")


    async def import_env(self, file: List[pc.UploadFile]):
        """Handle the upload of a file.

        Args:
            file: The uploaded file.
        """
        upload_data = await file[0].read()
        data = json.loads(upload_data)
        try:
            self.environments.clear()
            self.environments.extend([Environment(**d) for d in data])
        except:
            print_msg(self, "Error", "Invalid JSON")
            return

        
    def clear(self):
        self._reset_env(self)

    def del_env(self, env_id:str):
        logger.info(f"deleting {env_id}")
        
        if env_id == "":
            print_msg(self, "Info", "Please select a saved environment to delete")
            return
        
        if WEB_HOSTING:
            for env in self.environments:
                if env.id == int(env_id):
                    self.environments.remove(env)
                    break
        else:
            with pc.session() as session:
                row = session.query(Environment).filter(Environment.id == env_id)
                row.delete()
                session.commit()
            
        # self._reset_env(self, all=True)
        self.env_type = ""
        self.env_id = ""
        self.update_envs.fn(self)
        print_msg(self, "Success", "Environment deleted")
    