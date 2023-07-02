import asyncio
from app.utils.constants import *
from app.utils.functions import *
from .paperspace import EnvState
from typing import Dict

from reflex.event import EventHandler

import logging
logger = logging.getLogger(__name__)

def clean_exit_task(cls, name):
    if name in cls.task_in_progress:
        cls.task_in_progress[name] = False
    cls._task_to_interrupt.discard(name)
    cls._background_tasks.discard(name)
    cls._task_need_wait.discard(name)

class ControlPanelState(EnvState):
    task_in_progress: Dict[str, bool] = {
        "install_components": False,
        "upgrade_toolbox": False,
        "get_storage_size": False,
        "huggingface_upload": False,
        "compress_folder": False,
        "monitor": False,
        "shell": False,
        "sd_download": False,
        "llm_download": False,
    }
    task_progress: Dict[str, str] = {
        "install": "",
        "huggingface_upload": "",
        "compress": "",
        "monitor": "",
        "shell": "",
        "sd_download": "",
        "llm_download": "",
    }
    monitor_content: Dict[str, str] = {
        "component": "",
        "process": "",
        "gpu_usage": "",
    }
    huggingface_step: str = "select_mode"
    huggingface_mode: str = ""
    huggingface_token: str = ""
    huggingface_target_repo_id: str = ""
    huggingface_repo_is_private: bool = False
    huggingface_target_folder_path: str = ""
    huggingface_target_files: str = ""
    list_file_display: str = ""
    path_to_list: str = ""
    zip_target_path: str = "/storage/stable-diffusion/stable-diffusion-webui/outputs/"
    shell_command: str = ""
    shell_result: str = ""
    
    def set_task_in_progress(self, name:str):
        self.task_in_progress[name] = True
    
    def set_view_log(self, name, value=None):
        current_value = getattr(self, f"{name}_view_log")
        value = value if value is not None else not current_value
        setattr(self, f"{name}_view_log", value)
    
    async def _execute(self, command, success_msg=None, fail_msg=None, skip_msg=False):
        if self.extra_command_url == "":
            print_msg(self, "Error", "Please set the command server URL first.")
            return False
        else:
            try:
                result = await send_command(self, command)
                if result['code'] == 0:
                    if not skip_msg:
                        print_msg(self, "Success", success_msg.format(result['output']))
                    return result['output']
                else:
                    if not skip_msg:
                        print_msg(self, "Error", fail_msg.format(result['error']))
                    return result['error']
            except aiohttp.client_exceptions.ClientConnectorError:
                logger.exception("Unknown error")
                if not skip_msg:
                    print_msg(self, "Error", "Failed to connect to command server, maybe the URL is wrong?")
                return "Failed to connect to command server, maybe the URL is wrong?"
            except:
                if not skip_msg:
                    print_msg(self, "Error", "Unknown error")
                logger.exception("Fail to execute command: {}".format(command))
                return "Unknown error"
    
    @batch_update_state
    async def shell_execute(self):
        result = await self._execute(self.shell_command, skip_msg=True)
        self.shell_result = result
        clean_exit_task(self, "shell")
    
    @batch_update_state
    async def list_files_in_dir(self):
        command = f"find {self.path_to_list} -maxdepth 1"
        if self.extra_command_url == "":
            print_msg(self, "Error", "Please set the command server URL first.")
        else:
            try:
                result = await send_command(self, command)
                if result and result['code'] == 0:
                    self.list_file_display = result['output']
                else:
                    print_msg(self, "Error", "Failed to list files.\n {}".format(result['error']))
            except:
                logger.exception("Failed to list files")
                print_msg(self, "Error", "Unknown error")
    
    @batch_update_state
    async def upload_to_hf(self):
        env = f"HUGGINGFACE_TOKEN={self.huggingface_token} HF_TARGET_REPO={self.huggingface_target_repo_id}"
        if self.huggingface_repo_is_private:
            env += " HF_TARGET_REPO_PRIVATE=1"
        if self.huggingface_mode == "Upload Folder":
            env += f" HF_TARGET_FOLDER_PATH={self.huggingface_target_folder_path}"
        elif self.huggingface_mode == "Upload File":
            env += f" HF_TARGET_FILES={self.huggingface_target_files}"
        command = f"{env} bash /notebooks/huggingface/main.sh"
        # TODO change to async upload
        await self._execute(command, "Uploaded successfully.", "Failed to upload.\n {}")
        clean_exit_task(self, "huggingface_upload")

    async def upgrade_toolbox(self):
        await self._execute("cd /notebooks && git pull", "Toolbox upgraded successfully.", "Toolbox upgrade failed.\n {}")
        clean_exit_task(self, "upgrade_toolbox")
    
    async def get_storage_size(self):
        await self._execute("du -sh /storage", "Storage Usage: {}", "Failed to get storage size.\n {}")
        clean_exit_task(self, "get_storage_size")
        
        
    async def _process_log(self, stages, name, log_path, success_msg):
        await asyncio.sleep(REFRESH_RATE)
        state, result = await read_log(self, log_path)
        if state == "### ERROR ###":
            print_msg(self, "Error", "Unknown error")
            clean_exit_task(self, name)
            return False, -1, state, result
        if state != "":
            try:
                progress = None
                progress_index = stages.index(state)
                progress = int((progress_index + 1)/len(stages) * 100)
            except:
                logger.info("Unknown state: {}".format(state))
                return True, -1, state, result
            if progress == 100:
                print_msg(self, "Success", success_msg.format(result))
                clean_exit_task(self, name)
                return False, progress, state, result    
        return True, progress, state, result
    
        
    @batch_update_state
    async def download_model(self, name):
        log_path = f"/tmp/log/ui_{name}.log"
        stages = ["### Setting up Model Download ###", 
                  "### Downloading Models ###", 
                  "### Finished Model Download ###"]
            
        if name in self._background_tasks:
            ret, _, _, result  = await self._process_log(stages, name, log_path, "Finish Downloading model.\n")
            self.task_progress[name] = result
            # Either error or finish, end loop
            if ret == False:
                return
            return EventHandler(fn=self.download_model.func)(name)
        else:
            self._environment_variables = {}
            if name == "sd_download":
                self._add_t2i_models()
                script = f"/notebooks/utils/sd_model_download/main.sh"
            elif name == "llm_download":
                self._add_llm_models()
                script = f"/notebooks/utils/llm_model_download.sh"
            env = ""
            for key, value in self._environment_variables.items():
                env+= f"{key}={value} "
            command = f"{env} bash {script} > {log_path} 2>&1 &"
            try:
                result = await run_background_task(self, command)
                if result["code"] == -1:
                    print_msg(self, "Error", f"Failed to run {name}.\n {result['error']}")
            except:
                logger.exception(f"Failed to run {name}")
                print_msg(self, "Error", "Unknown error")
                
            self._background_tasks.add(name)
            return EventHandler(fn=self.download_model.func)(name)
    
    async def monitor(self):         
        if self.extra_command_url == "":
            print_msg(self, "Error", "Please set the command server URL first.")
            clean_exit_task(self, "monitor")
            return
               
        if "monitor" in self._task_to_interrupt:
            clean_exit_task(self, "monitor")
            return
        
        if "monitor" in self._task_need_wait:
            await asyncio.sleep(PAPERSPACE_MONITOR_INTERVAL)
            
        result = await self._execute("nvidia-smi", skip_msg=True)
        self.monitor_content['gpu_usage'] = result
        result = await self._execute("ps -ef", skip_msg=True)
        self.monitor_content['process'] = result
        result = await self._execute("python /notebooks/status_check.py", skip_msg=True)
        self.monitor_content['component'] = result
        
        self._task_need_wait.add("monitor")
        return self.monitor
    
    @batch_update_state
    async def compress_folder(self):
        name = "compress"
        log_path = "/tmp/log/ui_compress.log"
        stages = ["### Command received ###", "### Compressing ###", "### Done ###"]
            
        if name in self._background_tasks:
            ret, progress, state, result = await self._process_log(stages, name, log_path, "Compress successfully.\n {}")
            self.task_progress['compress'] = f"Progress: {progress}% Stage: {state.replace('#','').strip()}"
            # Either error or finish, end loop
            if ret == False:
                return
            return self.compress_folder
        elif self.zip_target_path == "":
            print_msg(self, "Error", "Target path cannot be empty.")
            clean_exit_task(self, "compress")
            return
        else:
            command = f"ZIP_TARGET_PATH={self.zip_target_path} bash /notebooks/utils/compress.sh > {log_path} 2>&1 &"
            try:
                result = await run_background_task(self, command)
                if result["code"] == -1:
                    print_msg(self, "Error", "Failed to compress folder.\n {}".format(result['error']))
            except:
                logger.exception("Failed to compress folder")
                print_msg(self, "Error", "Unknown error")
            # await self._execute(command, "Copressed successfully. Path to zip file: {}", "Failed to compress folder.\n {}")
            self._background_tasks.add("compress")
            return self.compress_folder
    
    # TODO: ask for comfirmation if action is start and process is already running
    @batch_update_state
    async def component_action(self, name, action):
        result = ""

        log_path = f"/tmp/log/ui_{name}_{action}.log"  
        # temp fix for a reflex issue
        # name = name.replace('"', ''); action = action.replace('"', '')    
        stages = ["### Command received ###", *getattr(self, f"{name}_substage")[action], "### Done ###"]
        status = getattr(self, f"add_{name}_enable", None)
        
        def exit_cleanup():
            self.set_action_status.fn(self, name, False)
            self._background_tasks.discard(f"{name}_{action}")
            setattr(self, f"{name}_action_log", result)
            
        if f"{name}_{action}" in self._background_tasks:
            await asyncio.sleep(REFRESH_RATE)
            state, result = await read_log(self, log_path)
            if state == "### ERROR ###":
                print_msg(self, "Error", f"Encountered error while {action} {name}.\n")
                exit_cleanup()
                return
            progress = None
            try:
                progress_index = stages.index(state)
                progress = int((progress_index + 1)/len(stages) * 100)
            except:
                setattr(self, f"{name}_action_progress",  "Progress: Unknown Stage: Unknown")
                setattr(self, f"{name}_action_log", result)
            if progress == 100:
                msg = f"Successfully completed {action} {name}."
                if action == 'start':
                    msg += "\nPlease reload cloudflare if using it without token"
                print_msg(self, "Success", msg)
                exit_cleanup() 
                return    
            setattr(self, f"{name}_action_progress",  f"Progress: {progress}% Stage: {state.replace('#','').strip()}")
            setattr(self, f"{name}_action_log", result)
            return EventHandler(fn=self.component_action.func)(name, action)
        
        elif f"{name}_{action}" in self._background_tasks:
            print_msg(self, "Error", "Already running")
            self.set_action_status.fn(self, name, False)
        elif status is False and action != "stop":
            print_msg(self, "Error", f"Please enable {name} first.")
            self.set_action_status.fn(self, name, False)
        elif status is None:
            print_msg(self, "Error", "action status is unknown")
            self.set_action_status.fn(self, name, False)
        elif name == "cloudflared" and action != "start" and self.extra_cloudflared_token != "":
            print_msg(self, "INFO", "Cloudflare with token does not support stop and restart, all configurations can be done on dashboard.")
            self.set_action_status.fn(self, name, False)
        else:
            check_env = getattr(self, f"_check_env_{name}", None)
            if check_env:
                result = check_env(add=True)
                if len(result) > 0:
                    msg = ""
                    for v in result:
                        msg += f"{v} is empty\n"
                    print_msg(self, "Error", msg)  
                    exit_cleanup()
                    return
            # prepare env
            if name == 'cloudflared' and action == 'reload':
                self._prepare_env(add=True)
                script = "/notebooks/cloudflare_reload.sh"
            else:                
                fn = getattr(self, f"_add_{name}", None)
                if fn is None:
                    print_msg(self, "Error", f"unable to find event handler for {name}")
                    exit_cleanup()
                    return
                else:
                    self._environment_variables = {}
                    fn(add=True)
                    script = f"/notebooks/{name}/control.sh"
            env = ""
            for key, value in self._environment_variables.items():
                env+= f"{key}={value} "
            command = f"{env} bash {script} {action} > {log_path} 2>&1 &"
            try:
                result = await run_background_task(self, command)
                if result["code"] == -1:
                    print_msg(self, "Error", f"Failed to {action} {name}.\n {result['error']}")
            except:
                logger.exception(f"Failed to {action} {name}")
                print_msg(self, "Error", "Unknown error")
                
            self._background_tasks.add(f"{name}_{action}")
            return EventHandler(fn=self.component_action.func)(name, action)
        
    # TODO: redo this
    async def install_components(self):
        if self.extra_command_url == "":
            print_msg(self, "Error", "Please set the command server URL first.")
        else:
            empty_var = []
            for k in self.event_handlers.keys():
                if k.startswith("_check_env"):
                    if result:= getattr(self, k)(self):
                        empty_var += result
            if len(empty_var) > 0:
                msg = ""
                for v in empty_var:
                    msg += f"{v} is empty\n"
                print_msg(self, "Error", msg)
            else:
                self._prepare_env(add=True)
                env = ""
                for key, value in self._environment_variables.items():
                    env+= f"{key}={value} "
                command = f"{env} bash /notebooks/entry.sh"
                await self._execute(command, "Components installed successfully.", "Components installation failed.\n {}")
        
        self.task_in_progress['install_components'] = False
        
    async def check_process_status(self, name):
        command = f"kill -0 $(cat /tmp/{name}.pid)"
        await self._execute(command, "Running", "Not running\n {}")
        self.set_action_status.fn(self, name, False)
                