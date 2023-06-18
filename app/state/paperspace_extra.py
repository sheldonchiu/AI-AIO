from app.utils.constants import *
from app.utils.functions import *
from typing import List, Dict, Optional
from .paperspace import NewEnvState

import logging
logger = logging.getLogger(__name__)

def set_value(self, key, value, condition):
    if value != condition:
        self._environment_variables[key] = value

def check_env(self, condition: bool, required_env_vars: List[str]):
    # defaults = cls.get_fields()
    if condition:
        empty_env_vars = [v for v in required_env_vars 
                            if getattr(self, v) == ""]
        if len(empty_env_vars) > 0:
            return empty_env_vars
    return []

class ToolState(NewEnvState):
    #### Cloudflare ####
    cloudflared_action_in_progress: bool = False
    cloudflared_action_progress: str = ""
    cloudflared_action_log: str = ""
    cloudflared_view_log: bool = False
    cloudflared_substage: Dict[str, List[str]] = {
        "start": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Cloudflare Tunnel"}).split("\n") if f],
        "stop": [],
        "reload": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Cloudflare Tunnel"}).split("\n") if f],
    }
    add_cloudflared_enable: bool = False
    extra_cloudflared_enable: bool = False
    extra_cloudflared_token: str = ""
    
    def _add_cloudflared(self, add=False):
        condition = self.add_cloudflared_enable if add else self.extra_cloudflared_enable
        if condition:
            self._add_script(self, "cloudflared")
            if self.extra_cloudflared_token == "":
                self._environment_variables['CF_TOKEN'] = 'quick'
            else:
                self._environment_variables['CF_TOKEN'] = self.extra_cloudflared_token
                
    #### Discord ####
    extra_discord_token: str = ""
    
    def _add_discord(self):
        set_value(self, "DISCORD_WEBHOOK_URL", self.extra_discord_token, "")
    
    #### Rclone ####
    rclone_action_in_progress: bool = False
    rclone_action_progress: str = ""
    rclone_action_log: str = ""
    rclone_view_log: bool = False
    rclone_substage: Dict[str, List[str]] = {
        "start": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Rclone"}).split("\n") if f],
        "stop": [],
        "reload": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Rclone"}).split("\n") if f],
    }
    add_rclone_enable: bool = False
    extra_rclone_enable: bool = False
    extra_rclone_username: str = ""
    extra_rclone_password: str = ""
    extra_rclone_serve_path: Optional[str] = ""
    
    def _add_rclone(self, add=False):
        condition = self.add_rclone_enable if add else self.extra_rclone_enable
        if condition:
            self._add_script(self, "rclone")
            self._environment_variables['RCLONE_USERNAME'] = self.extra_rclone_username
            self._environment_variables['RCLONE_PASSWORD'] = self.extra_rclone_password
            set_value(self, 'RCLONE_SERVE_PATH', self.extra_rclone_serve_path, "")

    #### Text to Image ####
    extra_t2i_model_list: str = ""
    extra_t2i_lora_list: str = ""
    extra_t2i_embedding_list: str = ""
    extra_t2i_vae_list: str = ""
    extra_t2i_controlnet_list: str = ""
    extra_t2i_hf_token: str = ""

    def _add_t2i_models(self):
            set_value(self, 'MODEL_LIST', self.extra_t2i_model_list, "")
            set_value(self, 'LORA_LIST', self.extra_t2i_lora_list, "")
            set_value(self, 'EMBEDDING_LIST', self.extra_t2i_embedding_list, "")
            set_value(self, 'VAE_LIST', self.extra_t2i_vae_list, "")
            set_value(self, 'CONTROLNET_LIST', self.extra_t2i_controlnet_list, "")
            set_value(self, 'HF_TOKEN', self.extra_t2i_hf_token, "")

    #### Stable Diffusion WebUI ####
    sd_webui_action_in_progress: bool = False
    sd_webui_action_progress: str = ""
    sd_webui_action_log: str = ""
    sd_webui_view_log: bool = False
    sd_webui_substage: Dict[str, List[str]] = {
        "start": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Stable Diffusion WebUI", "download_model": True}).split("\n") if f],
        "stop": [],
        "reload": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Stable Diffusion WebUI", "download_model": True}).split("\n") if f],
        "download_model": ["### Downloading Model for Stable Diffusion WebUI ###"],
    }
    add_sd_webui_enable: bool = False
    extra_sd_webui_enable: bool = False

    extra_sd_webui_auth: str= ""
    extra_sd_webui_gradio_share: bool = False
    extra_sd_webui_xformers: bool = False
    extra_sd_webui_update: bool = False

    def _add_sd_webui(self, add=False):
        condition = self.add_sd_webui_enable if add else self.extra_sd_webui_enable
        if condition:
            self._add_script(self, "sd_webui")
            self._add_t2i_models(self)
            set_value(self, 'GRADIO_AUTH', self.extra_sd_webui_auth, "")
            set_value(self, 'GRADIO_LINK', self.extra_sd_webui_gradio_share, False)
            set_value(self, 'ACTIVATE_XFORMERS', self.extra_sd_webui_xformers, False)
            if self.extra_sd_webui_update:
                set_value(self, "SD_WEBUI_UPDATE_REPO", "auto", "")

    #### Stable Diffusion Volta ####
    sd_volta_action_in_progress: bool = False
    sd_volta_action_progress: str = ""
    sd_volta_action_log: str = ""
    sd_volta_view_log: bool = False
    sd_volta_substage: Dict[str, List[str]] = {
        "start": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Stable Diffusion Volta", "download_model": True}).split("\n") if f],
        "stop": [],
        "reload": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Stable Diffusion Volta", "download_model": True}).split("\n") if f],
        "download_model": ["### Downloading Model for Stable Diffusion Volta ###"],
    }
    add_sd_volta_enable: bool = False
    extra_sd_volta_enable: bool = False
    extra_sd_volta_update: bool = False

    def _add_sd_volta(self, add=False):
        condition = self.add_sd_volta_enable if add else self.extra_sd_volta_enable
        if condition:
            self._add_script(self, "sd_volta")
            self._add_t2i_models(self)
            if self.extra_sd_volta_update:
                set_value(self, "SD_VOLTA_UPDATE_REPO", "auto", "")
    
    #### Stable Diffusion Comfy ####       
    sd_comfy_action_in_progress: bool = False
    sd_comfy_action_progress: str = ""
    sd_comfy_action_log: str = ""
    sd_comfy_view_log: bool = False
    sd_comfy_substage: Dict[str, List[str]] = {
        "start": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Stable Diffusion Comfy", "download_model" : True}).split("\n") if f],
        "stop": [],
        "reload": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Stable Diffusion Comfy", "download_model" : True}).split("\n") if f],
    }
    extra_sd_comfy_enable: bool = False
    add_sd_comfy_enable: bool = False
    extra_sd_comfy_update: bool = False
    extra_sd_comfy_required_env_vars: List[str] = [""]
    
    def _add_sd_comfy(self, add=False):
        condition = self.add_sd_comfy_enable if add else self.extra_sd_comfy_enable
        if condition:
            self._add_script(self, "sd_comfy")
            self._add_t2i_models(self)
            if self.extra_sd_comfy_update:
                set_value(self, "SD_COMFY_UPDATE_REPO", "auto", "")

    #### Minio ####
    minio_action_in_progress: bool = False
    minio_action_progress: str = ""
    minio_action_log: str = ""
    minio_view_log: bool = False
    minio_substage: Dict[str, List[str]] = {
        "start": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Minio"}).split("\n") if f],
        "stop": [],
        "reload": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Minio"}).split("\n") if f],
    }
    add_minio_enable: bool = False
    extra_minio_enable: bool = False
    extra_minio_host: str = ""
    extra_minio_access_key: str = ""
    extra_minio_secret_key: str = ""
    extra_minio_mirror_path: Optional[str] = ""
    extra_minio_mirror_bucket: Optional[str] = ""
    extra_minio_required_env_vars: List[str] = ["extra_minio_host", "extra_minio_access_key", "extra_minio_secret_key"]
    
    def _check_env_minio(self, add=False):
        return check_env(self, 
                         self.add_minio_enable if add else self.extra_minio_enable,
                         self.extra_minio_required_env_vars
                        )
    
    def _add_minio(self, add=False):
        condition = self.add_minio_enable if add else self.extra_minio_enable
        if condition:
            self._add_script(self, "minio")
            self._environment_variables['S3_HOST_URL'] = self.extra_minio_host
            self._environment_variables['S3_ACCESS_KEY'] = self.extra_minio_access_key
            self._environment_variables['S3_SECRET_KEY'] = self.extra_minio_secret_key
            set_value(self, 'S3_MIRROR_PATH', self.extra_minio_mirror_path, "")
            set_value(self, 'S3_MIRROR_TO_BUCKET', self.extra_minio_mirror_bucket, "")

    #### FastChat ###
    fastchat_action_in_progress: bool = False
    fastchat_action_progress: str = ""
    fastchat_action_log: str = ""
    fastchat_view_log: bool = False
    fastchat_substage: Dict[str, List[str]] = {
        "start": [f for f in STAGE_BASE_TEMPLATE.render({'title': "FastChat", "download_model" : True}).split("\n") if f],
        "stop": [],
        "reload": [f for f in STAGE_BASE_TEMPLATE.render({'title': "FastChat", "download_model" : True}).split("\n") if f],
    }
    add_fastchat_enable: bool = False
    extra_fastchat_enable: bool = False
    extra_fastchat_models: Dict[str, bool] = {model: False for model in FASTCHAT_MODELS}
    
    
    def update_fastchat_model_selecion(self, args: Dict[str, str]):
        update_checkbox_selecion(self.extra_fastchat_models, args)
    
    def _add_fastchat(self, add=False):
        condition = self.add_fastchat_enable if add else self.extra_fastchat_enable
        if condition:
            self._add_script(self, "fastchat")
            self._environment_variables['FASTCHAT_MODEL'] = ",".join([model for model, cond in self.extra_fastchat_models.items() if cond])
            
    #### TextGen ####
    textgen_action_in_progress: bool = False
    textgen_action_progress: str = ""
    textgen_action_log: str = ""
    textgen_view_log: bool = False
    textgen_substage: Dict[str, List[str]] = {
        "start": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Text generation Webui", "download_model" : True}).split("\n") if f],
        "stop": [],
        "reload": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Text generation Webui", "download_model" : True}).split("\n") if f],
    }
    add_textgen_enable: bool = False
    extra_textgen_enable: bool = False
    extra_textgen_models: Dict[str, bool] = {model: False for model in TEXTGEN_MODELS}
    
    def update_textgen_model_selecion(self, args: Dict[str, str]):
        update_checkbox_selecion(self.extra_textgen_models, args)
    
    def _add_textgen(self, add=False):
        condition = self.add_textgen_enable if add else self.extra_textgen_enable
        if condition:
            self._add_script(self, "textgen")
            self._environment_variables['TEXTGEN_MODEL'] = ",".join([model for model, cond in self.extra_textgen_models.items() if cond])
            
            
    ### Command Server ####
    extra_command_enable: bool = False
    extra_command_url: str = ""
    extra_command_user: str = ""
    extra_command_password: str = ""
    extra_command_required_env_vars: List[str] = ["extra_command_user", "extra_command_password"]
    
    def _check_env_command(self,add=False):
        return check_env(self, self.extra_command_enable, self.extra_command_required_env_vars)
    
    def _add_command(self, add=False):
        if self.extra_command_enable:
            self._add_script(self, "command")
            self._environment_variables['COMMAND_USERNAME'] = self.extra_command_user
            self._environment_variables['COMMAND_PASSWORD'] = self.extra_command_password

    ### Image Browser ####
    image_browser_action_in_progress: bool = False
    image_browser_action_progress: str = ""
    image_browser_action_log: str = ""
    image_browser_view_log: bool = False
    image_browser_substage: Dict[str, List[str]] = {
        "start": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Image Browser", "download_model" : False}).split("\n") if f],
        "stop": [],
        "reload": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Image Browser", "download_model" : False}).split("\n") if f],
    }
    extra_image_browser_enable: bool = False
    add_image_browser_enable: bool = False
    extra_image_browser_key: str = ""
    extra_image_browser_required_env_vars: List[str] = ["extra_image_browser_key"]
    
    def _check_env_image_browser(self, add=False):
        return check_env(self, 
                        self.add_image_browser_enable if add else self.extra_image_browser_enable,
                        self.extra_image_browser_required_env_vars
                        )
    
    def _add_image_browser(self, add=False):
        condition = self.add_image_browser_enable if add else self.extra_image_browser_enable
        if condition:
            self._add_script(self, "image_browser")
            self._environment_variables['IMAGE_BROWSER_KEY'] = self.extra_image_browser_key

    ### Template ####     
    # {{ name }}_action_in_progress: bool = False
    # {{ name }}_action_progress: str = ""
    # {{ name }}_action_log: str = ""
    # {{ name }}_view_log: bool = False
    # {{ name }}_substage: Dict[str, List[str]] = {
    #     "start": [f for f in STAGE_BASE_TEMPLATE.render({'title': "{{ title }}", "download_model" : False}).split("\n") if f],
    #     "stop": [],
    #     "reload": [f for f in STAGE_BASE_TEMPLATE.render({'title': "{{ title }}", "download_model" : False}).split("\n") if f],
    # }
    # extra_{{ name }}enable: bool = False
    # add_{{ name }}_enable: bool = False
    # extra_{{ name }}_required_env_vars: List[str] = [""]
    
    # def _check_env_command(self):
    #     return check_env(self, self.extra_image_browser_enable, self.extra_image_browser_required_env_vars)
    
    # def _add_command(self, add=False):
    #     condition = self.add_{{ name }}_enable if add else self.extra_{{ name }}_enable
    #     if condition:
    #         self._add_script(self, "{{ name }}")
    #         self._environment_variables['IMAGE_BROWSER_KEY'] = self.extra_image_browser_key
