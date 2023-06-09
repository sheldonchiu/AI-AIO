from itertools import islice
import asyncio
import aiohttp
import re
import hashlib
import inspect
import functools
from typing import Dict, List, Any
import json
from app.utils.constants import Page, ALL_GPU

import logging
logger = logging.getLogger(__name__)

def print_msg(cls, header: str, msg: str) -> None:
    """
    Sets properties of a class instance to display an alert message.

    Args:
        cls: The class instance to set properties on.
        header: The header text for the alert message.
        msg: The body text for the alert message.

    Returns:
        None.
    """
    cls.alert_header = header
    cls.alert_msg = msg
    cls.show_alert = True
    
async def send_command(cls, command: str):
    """
    Sends a command to a remote server using the execute endpoint.

    Args:
        cls (object): The class object.
        command (str): The command to send.

    Returns:
        dict: A dictionary containing the result of the command execution. The dictionary has the following keys:
        - code: The exit code of the command.
        - output: The standard output of the command.
        - error: The standard error of the command, if any.

    Raises:
        None.
    """
    url = f"{cls.extra_command_url}/execute"
    auth = aiohttp.BasicAuth(cls.extra_command_user,
                             cls.extra_command_password)
    data = {'command': command}
    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json'}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, auth=auth, headers=headers, data=json.dumps(data)) as response:
            if response.status == 200:
                return await response.json()
            else:
                logger.error(
                    f"Send Command fail: {response.status} {response.reason}")
                return {"code": -1, "output": "", "error": f"{response.status} {response.reason}"}


async def run_background_task(cls, command: str):
    """
    Executes a command in the background on a remote server using the run endpoint.

    Args:
        cls (object): The class object.
        command (str): The command to execute in the background.

    Returns:
        dict: A dictionary containing the result of the command execution. The dictionary has the following keys:
        - code: The exit code of the command.
        - output: The standard output of the command.
        - error: The standard error of the command, if any.

    Raises:
        None.
    """
    url = f"{cls.extra_command_url}/run"
    auth = aiohttp.BasicAuth(cls.extra_command_user,
                             cls.extra_command_password)
    data = {'command': command}
    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json'}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, auth=auth, headers=headers, data=json.dumps(data)) as response:
            if response.status == 200:
                return await response.json()
            else:
                logger.error(
                    f"Send Command fail: {response.status} {response.reason}")
                return {"code": -1, "output": "", "error": f"{response.status} {response.reason}"}


async def read_log(cls, log_path) -> tuple:
    """
    Reads the contents of a log file and returns the last substring matching the pattern '### * ###',
    along with the entire log contents.

    Args:
        cls (object): The class object.
        log_path (str): The path to the log file to read.

    Returns:
        tuple: A tuple containing the last substring matching the pattern '### * ###' found in the log file,
        and the entire log contents as a string. If an error occurs, returns a tuple with the string "Error"
        and a value of None.

    Raises:
        None.
    """
    try:
        result = await send_command(cls, f"cat {log_path}")
        if result and result['code'] == 0:
            matches = re.findall(r"###\s.*?\s###", result['output'])
            target = matches[-1] if len(matches) > 0 else ""
            return target, result['output']
        else:
            print_msg(cls, "Error", f"Failed to read log\n {result['error']}")
            return "Error", None
    except:
        logger.exception(f"Failed to read log {log_path}")
        print_msg(cls, "Error", "Unknown error")
        return "Error", None
    
def convert_to_js_id(s: str):
    """
    Convert a string into a valid JavaScript id.
    """
    hash = hashlib.md5(s.encode('utf-8')).hexdigest()
    # Replace all non-alphanumeric characters with underscores
    s = re.sub(r'\W+', '_', s)
    
    # Remove leading and trailing underscores
    s = s.strip('_')
    
    # Ensure that the id starts with a letter
    if not s[0].isalpha():
        s = 'id_' + s
        
    s += '_' + hash[:4]
    
    return s

def decode_and_insert_env(cls, key, value):
    # Split the string by "__" to separate the parts
    parts = key.split("__")
    
    # If there are only two parts, assume it's a normal variable and return the second part
    if len(parts) == 2:
        name = parts[1] 
        if hasattr(cls, name):
            setattr(cls, name , value)
    
    # If there are three parts, assume it's a dictionary and return the second and third parts as a tuple
    elif len(parts) == 3:
        attr_name = parts[1]
        if hasattr(cls, attr_name):
            try:
                key_name = int(parts[2])
                d = getattr(cls, attr_name)
                key_name, _ = next(islice(d.items(), key_name, key_name+1))
                d[key_name] = value
            except:
                logger.error(f"Failed to decode and insert env {key} {value}")
                return
    
    # If there are more than three parts, assume the first part is "ref_" followed by the page name,
    # and return the rest of the parts as a list
    # elif len(parts) > 3:
    #     return [part for part in parts[2:]]
    
def batch_update_state(func):
    # a decorator to load kwargs to env
    signature = inspect.signature(func)
    parameters = list(signature.parameters.values())
    parameters.append(inspect.Parameter(
        'env', inspect.Parameter.POSITIONAL_OR_KEYWORD, default={}, annotation=Dict[str, Any]))
    new_signature = signature.replace(parameters=parameters)
            
    def wrapper_sync(self, *args, **kwargs):
        env = kwargs.pop('env', {})
        for e in env:
            if (value:= e.get("value", None)) is None:
                continue
            decode_and_insert_env(self, e['refName'], value)
        return func(self, *args, **kwargs)
    
    async def wrapper_async(self, *args, **kwargs):
        env = kwargs.pop('env', {})
        for e in env:
            if (value:= e.get("value", None)) is None:
                continue
            decode_and_insert_env(self, e['refName'], value)
        return await func(self, *args, **kwargs)    

    wrapper = wrapper_async if asyncio.iscoroutinefunction(func) else wrapper_sync
    wrapper.__signature__ = new_signature
    functools.update_wrapper(wrapper, func)
    return wrapper
        

# def convert_to_js_dict(key_list, value: str, prefix:str=""):
#     output = []
#     for key in key_list:
#         if key.type_ is Dict:
            
#     return '{' + ','.join([f"'{key}': ref_{prefix}{convert_to_js_id(key)}.current.{value}" for key in key_list]) + '}'

def update_checkbox_selecion(var: Dict[str, bool], args: Dict[str, str]):
    for selection in var.keys():
        if selection in args:
            var[selection] = args[selection]
            
def get_ref_name(page_id, name):
    return f"ref_{get_page_id_prefix(page_id)}{name}"
            
def get_page_id_prefix(page_id):
    if page_id == Page.main:
        return "main__"
    elif page_id == Page.control_panel:
        return "control_panel__"
    
    
            
