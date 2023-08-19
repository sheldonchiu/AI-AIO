import asyncio
import json
import time

import logging
logger = logging.getLogger(__name__)

from collections import OrderedDict
import typing
from typing import Dict, List, Optional, Set, Union

import gradient

import reflex as rx
from reflex import constants
from reflex.utils import types
from reflex.event import EventHandler

from sqlmodel import Field, select

from app.app import BaseState
from app.utils.constants import *
from app.utils.functions import *
from app.backend.paperspace_util import Paperspace_client

class Environment(rx.Model, table=True):
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
    """Class representing the state of Paperspace."""

    power_light: str = "red-700"  # color of the power light
    power_button: str = "Start"  # text on the power button
    show_progress_for_start_button: bool = False  # whether to show progress for the start button
    environments: List[Environment] = []  # list of environments
    env_type: str = ""  # type of environment
    retry_count: int = 0  # number of retries
    retry_str = ""  # retry string
    _task_to_interrupt: Set[str] = set()  # set of tasks to interrupt
    _task_need_wait: Set[str] = set()  # set of tasks that need to wait
    _background_tasks: Set[str] = set()  # set of background tasks

    @rx.var
    def display_retry_count(self) -> bool:
        """Whether to display the retry count."""
        return self.retry_count > 0

    @rx.var
    def retry_count_str(self) -> str:
        """String representation of the retry count."""
        return f"{self.retry_str}: {self.retry_count}"

    @rx.var
    def is_env_selected(self) -> bool:
        """Whether an environment is selected."""
        return self.env_type != ""

    @rx.var
    def get_env_download_link(self) -> str:
        """Get the download link for the environment."""
        return f"{constants.API_URL}/download_env/{self.get_token()}"

    def interrupt_task(self, name:str):
        """Interrupt a task."""
        self._task_to_interrupt.add(name)

    def update_envs(self):
        """Update the list of environments."""
        if WEB_HOSTING == False:
            try:
                with rx.session() as session:
                    self.environments.clear()
                    self.environments.extend(session.exec(select(Environment)).all())
            except:
                print_msg(self, "Error", "Failed to fetch environments from database.")

    def _toggle_power(self, status):
        """Toggle the power status."""
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
        """
        Cleanly exits a task by removing it from various internal sets.

        Parameters:
            name (str): The name of the task to be cleaned.

        Returns:
            None
        """
        self._task_to_interrupt.discard(name)
        self._background_tasks.discard(name)
        self._task_need_wait.discard(name)
    
    def _reset_env(self, all=False):
        """
        Resets the environment variables to their default values.

        Parameters:
            all (bool): If True, resets all variables including the 'env_type' variable. If False, only resets variables starting with 'env_' or 'extra_'.
        
        Returns:
            None
        """
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
            self._add_command()
            
        self._add_discord()
        # self._add_cloudflared(add)
        
        self._add_sd_webui(add)
        self._add_sd_comfy(add)
        self._add_sd_fooocus(add)
        self._add_preprocess(add)
        self._add_sd_volta(add)
        self._add_image_browser(add)
        
        self._add_fastchat(add)
        self._add_textgen(add)
        self._add_flowise(add)
        self._add_langflow(add)
        
        self._add_musicgen(add)
        self._add_kosmos2(add)
        
        self._add_minio(add)
        self._add_rclone(add)
                    
    def _validate_env(self, validate_gpu= False) -> bool:
        """
        Validate the environment settings.

        Args:
            validate_gpu (bool): Flag indicating whether to validate GPU settings.
        
        Returns:
            bool: True if the environment is valid, False otherwise.
        """
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
        """
        Sets the status of an action.

        Parameters:
            name (str): The name of the action.
            status (bool): The status of the action.

        Returns:
            None
        """
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
        """
        This function starts or stops a notebook based on the value of `self.power_button`.
        If `self.power_button` is set to "Stop", it stops the notebook and returns `None`.
        If `self.power_button` is not set to "Stop", it validates the environment and
        starts the notebook.

        Returns:
            Union[None, EventHandler]: The `start_notebook` coroutine if `self.power_button` is not set to "Stop", otherwise `None`.
        """

        self.retry_count = 0
        self._client = Paperspace_client(self.env_api_key)
        
        if self.power_button == "Stop":
            self._client.notebooks_client.stop(self.env_notebook_id)
            self._toggle_power(False)
            self.show_progress_for_start_button = False
            self.notebook_url = ""
            return
        
        if not self._validate_env(validate_gpu=True):
            self.show_progress_for_start_button = False
            return
        # do it this way to keep the gpu order, try best gpu first
        self._gpu_priority = [gpu for gpu in self.gpu_list.keys() if self.gpu_list[gpu]]
        self._start_time = time.time()
        self._background_tasks.add("start_notebook")
        return self.start_notebook
        
    async def start_notebook(self) -> Union[None, EventHandler]:
        """
        Starts the notebook asynchronously.

        Returns:
            Union[None, EventHandler]: If "start_notebook" is in _task_to_interrupt, cleans up and returns None.
            If "start_notebook" is in _task_need_wait, waits for PAPERSPACE_START_RATE seconds and returns self.start_notebook.
            If there is no available GPU, logs a message, increments the retry count, adds "start_notebook" to _task_need_wait, and returns self.start_notebook.
            If the environment type is "existing", starts the notebook with the specified notebook ID and GPU, and returns self.check_notebook_status.
            If the environment type is "new", prepares the environment, creates a project, deletes the notebook from the project, and creates a new notebook with the specified parameters. Sets optional parameters if provided. Returns self.check_notebook_status.
            If a ResourceFetchingError occurs and the error message contains "We are currently out of capacity", logs a warning message, increments the retry count, adds "start_notebook" to _task_need_wait, and returns self.start_notebook.
            If any other exception occurs, logs an exception message, increments the retry count, adds "start_notebook" to _task_need_wait, and returns self.start_notebook.
            If any exception occurs during the execution of the function, prints an error message, turns off the power, sets show_progress_for_start_button to False, and cleans up.
        """
        if "start_notebook" in self._task_to_interrupt:
            self._clean_exit_task("start_notebook")
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
                self.retry_str = "No GPU, retrying"
                self.retry_count += 1
                self._task_need_wait.add("start_notebook")
                return self.start_notebook
            try:
                if self.env_type == 'existing':
                    self.env_notebook_id = self._client.start_notebook(self.env_notebook_id, gpu)
                elif self.env_type == 'new':
                    self._prepare_env()
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
            except gradient.api_sdk.sdk_exceptions.ResourceFetchingError as e:
                if "We are currently out of capacity" in str(e):
                    logger.warning("Out of capacity")
                    self.retry_str = "No GPU, retrying"
                    self.retry_count += 1
                    self._task_need_wait.add("start_notebook")
                    return self.start_notebook
                # don't continue if encounter this error
                raise
            except Exception as e:
                # Sometimes the GPU is not available after the first check
                logger.exception("Failed to start notebook")
                self.retry_str = "Failed to start, retrying"
                self.retry_count += 1
                self._task_need_wait.add("start_notebook")
                return self.start_notebook
        except Exception as e:
            print_msg(self, "Error", str(e))
            self._toggle_power(False)          
            self.show_progress_for_start_button = False
            self._clean_exit_task("start_notebook")
        
    async def check_notebook_status(self) -> Union[None, EventHandler]:    
        
        if "start_notebook" in self._task_to_interrupt:
            self._clean_exit_task("start_notebook")
            self.show_progress_for_start_button = False
            self.retry_count = 0
            return
        
        if "start_notebook" in self._task_need_wait:
            await asyncio.sleep(PAPERSPACE_START_RATE)
            
        notebook = self._client.get_notebook_detail(self.env_notebook_id)
        if notebook.state == "Running":
            self._toggle_power(True)
            if WEB_HOSTING == False and self.env_id != "":
                with rx.session() as session:
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
            if self.command_url == "":
                self.command_url = self.notebook_url.split('?')[0] + '/command/'

        elif notebook.state == "Failed":
            logger.info("Notebook failed to start, maybe their platform is down")
            print_msg(self, "Error", "Notebook failed to start, maybe their platform is down, please retry later")
            # continue to clean up
        else:
            logger.info("Waiting for Notebook to start, retrying in 5 seconds")
            self.retry_str = "Waiting for Notebook to start"
            self.retry_count += 1
            self._task_need_wait.add("start_notebook")
            return self.check_notebook_status
        
        self.show_progress_for_start_button = False
        self.retry_count = 0
        self._clean_exit_task("start_notebook")
        
    @rx.var
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
    
    @batch_update_state
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
            try:
                self._toggle_power(False)
                for notebook in client.get_notobooks_by_project_name(f"{self.env_name} From Toolbox"):             
                    if notebook.state == "Running":
                        self.notebook_url = client.get_notebook_url(notebook)
                        if self.command_url == "":
                            self.command_url = self.notebook_url.split('?')[0] + '/command/'
                        self.env_project_id = notebook.project_handle
                        self.env_notebook_id = notebook.id
                        self._toggle_power(True)
                        return
            except:
                logger.exception("Failed to get notebook status")
                print_msg(self, "Error", "Failed to get notebook status")
        except:
            logger.exception("Failed to sync")
            print_msg(self, "Error", "Failed to sync, please check if the API key is correct")
            
    def load_env(self, selected_id: str):
        if selected_id == "":
            self.env_type = ""
            self._reset_env()
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
    def copy_env(self):
        self.env_name = f"{self.env_name}_copy"
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
            data = create_env()
            if WEB_HOSTING:
                id = get_next_id(self.environments)
                data.id = id
                self.env_id = str(id)
                self.environments.append(data)
            else:
                with rx.session() as session:
                    session.add(data)
                    session.commit()
                    self.env_id = str(data.id)
                    self.update_envs.fn(self)
        except:
            print_msg(self, "Error", "Internal error, unable to copy environment")
            return

        print_msg(self, "Success", "Environment Copied.")       
    
    @batch_update_state
    def save_env(self):
        """
        Save the environment.

        This function is responsible for saving the environment. It creates an environment object using the variables stored in `self.vars` that start with "env_" but are not "env_id". The extra information is stored as a JSON string in the "extra_info" field of the environment object.

        If `WEB_HOSTING` is `True`, the environment object is created and updated in the `self.environments` list based on `self.env_id`. If `self.env_id` is empty, a new ID is generated and assigned to the environment object and it is appended to the `self.environments` list.

        If `WEB_HOSTING` is `False`, a session is started and the environment object is updated or added to the database based on `self.env_id`. If `self.env_id` is empty or the corresponding row in the database is not found, a new environment object is created and added to the database.

        After saving the environment, the `self.update_envs.fn` function is called to update the environments.

        Raises:
            Any exception that occurs during the saving of the environment will result in an "Internal error, unable to save environment" message being printed.

        Returns:
            None. If the environment is successfully saved, a "Environment saved." message is printed.
        """
        def create_env():
            # Create a dictionary of attributes for the environment object
            kwargs = {
                key: getattr(self, key)
                for key in self.vars.keys()
                if key.startswith("env_") and key not in ["env_id"]
            }

            # Add extra_info attribute to the dictionary, which is a JSON string
            kwargs["extra_info"] = json.dumps({
                key: getattr(self, key)
                for key in self.vars.keys()
                if key.startswith("extra_")
            })

            # Create and return the Environment object with the specified attributes
            return Environment(**kwargs)

        try:
            # Check if the code is running in a web hosting environment
            if WEB_HOSTING:
                # Create an environment object
                data = create_env()

                # Check if an environment is selected
                if self.env_id != "":
                    # Update the existing environment with the new data
                    for idx, env in enumerate(self.environments):
                        if env.id == int(self.env_id):
                            data.id = env.id
                            self.environments[idx] = data
                            break
                else:
                    # Generate a new id for the environment
                    id = get_next_id(self.environments)
                    data.id = id
                    self.env_id = str(id)
                    # Add the new environment to the list
                    self.environments.append(data)
            else:
                # Perform the following operations in a database session
                with rx.session() as session:
                    # Check if an environment is selected
                    if self.env_id != "":
                        # Get the row to edit from the database
                        row_to_edit = session.query(Environment).filter(
                            Environment.id == self.env_id).first()
                        if row_to_edit is not None:
                            # Create a dictionary to store extra_info attributes
                            extra_info = {}
                            # Loop through all the attributes
                            for key in self.vars.keys():
                                # Get the value of the attribute
                                value = getattr(self, key, None)
                                if value is not None:
                                    if key.startswith("env_") and key != "env_id":
                                        # Update the attribute in the row_to_edit object
                                        setattr(row_to_edit, key, value)
                                    elif key.startswith("extra_"):
                                        # Add the attribute to the extra_info dictionary
                                        extra_info[key] = value
                            # Convert the extra_info dictionary to a JSON string
                            row_to_edit.extra_info = json.dumps(extra_info)
                            # Commit the changes to the database
                            session.commit()
                    else:
                        # Create a new environment object
                        data = create_env()
                        # Add the environment object to the database
                        session.add(data)
                        session.commit()
                        self.env_id = str(data.id)

                    # Call the update_envs function
                    self.update_envs.fn(self)
        except:
            # Print an error message if an exception occurs
            print_msg(self, "Error", "Internal error, unable to save environment")
            return

        # Print a success message
        print_msg(self, "Success", "Environment saved.")



    async def import_env(self, file: List[rx.UploadFile]):
        """Handle the upload of a file.

        Args:
            file: The uploaded file.
        """ 
        upload_data = await file[0].read()
        data = json.loads(upload_data)
        try:
            env = [Environment(**d) for d in data]
            for e in env:
                e.id = get_next_id(self.environments)
            self.environments.extend(env)
        except:
            print_msg(self, "Error", "Invalid JSON")
            return

        
    def clear(self):
        self._reset_env()

    def del_env(self, env_id:str):
        logger.info(f"deleting {env_id}")
        
        if env_id == "":
            print_msg(self, "Info", "Please select a saved environment to delete")
            return
        
        for env in self.environments:
            if env.id == int(env_id):
                self.environments.remove(env)
                break
            
        if not WEB_HOSTING:
            with rx.session() as session:
                row = session.query(Environment).filter(Environment.id == env_id)
                row.delete()
                session.commit()
            
        # self._reset_env(all=True)
        self.env_type = ""
        self.env_id = ""
        print_msg(self, "Success", "Environment deleted")
    
