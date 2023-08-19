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
    # cloudflared_action_in_progress: bool = False
    # cloudflared_action_progress: str = ""
    # cloudflared_action_log: str = ""
    # cloudflared_view_log: bool = False
    # cloudflared_substage: Dict[str, List[str]] = {
    #     "start": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Cloudflare Tunnel"}).split("\n") if f],
    #     "stop": [],
    #     "reload": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Cloudflare Tunnel"}).split("\n") if f],
    # }
    # add_cloudflared_enable: bool = False
    # extra_cloudflared_enable: bool = False
    # extra_cloudflared_token: str = ""

    # def _add_cloudflared(self, add=False):
    #     condition = self.add_cloudflared_enable if add else self.extra_cloudflared_enable
    #     if condition:
    #         # cloudflare start logic will be handled by the script, don't need to run add_script
    #         if self.extra_cloudflared_token == "":
    #             self._environment_variables['CF_TOKEN'] = 'quick'
    #         else:
    #             self._add_script("cloudflared")
    #             self._environment_variables['CF_TOKEN'] = self.extra_cloudflared_token

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
    extra_rclone_args: str = ""

    def _add_rclone(self, add=False):
        condition = self.add_rclone_enable if add else self.extra_rclone_enable
        if condition:
            self._add_script("rclone")
            self._environment_variables['RCLONE_USERNAME'] = self.extra_rclone_username
            self._environment_variables['RCLONE_PASSWORD'] = self.extra_rclone_password
            self._environment_variables['EXTRA_RCLONE_ARGS'] = self.extra_rclone_args
            set_value(self, 'RCLONE_SERVE_PATH',
                      self.extra_rclone_serve_path, "")

    #### Text to Image ####
    extra_t2i_model_list: str = ""
    extra_t2i_lora_list: str = ""
    extra_t2i_embedding_list: str = ""
    extra_t2i_vae_list: str = ""
    extra_t2i_controlnet_list: str = ""
    extra_t2i_upscaler_list: str = ""
    extra_t2i_hf_token: str = ""

    def _add_t2i_models(self):
        set_value(self, 'MODEL_LIST', self.extra_t2i_model_list, "")
        set_value(self, 'LORA_LIST', self.extra_t2i_lora_list, "")
        set_value(self, 'EMBEDDING_LIST', self.extra_t2i_embedding_list, "")
        set_value(self, 'VAE_LIST', self.extra_t2i_vae_list, "")
        set_value(self, 'CONTROLNET_LIST', self.extra_t2i_controlnet_list, "")
        set_value(self, 'UPSCALER_LIST', self.extra_t2i_upscaler_list, "")
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
    }
    add_sd_webui_enable: bool = False
    extra_sd_webui_enable: bool = False

    extra_sd_webui_auth: str = ""
    extra_sd_webui_update: bool = False
    extra_sd_webui_args: str = ""

    def _add_sd_webui(self, add=False):
        condition = self.add_sd_webui_enable if add else self.extra_sd_webui_enable
        if condition:
            self._add_script("sd_webui")
            self._add_t2i_models()
            set_value(self, 'SD_WEBUI_GRADIO_AUTH', self.extra_sd_webui_auth, "")
            self._environment_variables['EXTRA_SD_WEBUI_ARGS'] = self.extra_sd_webui_args
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
    extra_sd_volta_args: str = ""

    def _add_sd_volta(self, add=False):
        condition = self.add_sd_volta_enable if add else self.extra_sd_volta_enable
        if condition:
            self._add_script("sd_volta")
            self._add_t2i_models()
            self._environment_variables['EXTRA_SD_VOLTA_ARGS'] = self.extra_sd_volta_args
            if self.extra_sd_volta_update:
                set_value(self, "SD_VOLTA_UPDATE_REPO", "auto", "")

    #### Stable Diffusion Comfy ####
    sd_comfy_action_in_progress: bool = False
    sd_comfy_action_progress: str = ""
    sd_comfy_action_log: str = ""
    sd_comfy_view_log: bool = False
    sd_comfy_substage: Dict[str, List[str]] = {
        "start": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Stable Diffusion Comfy", "download_model": True}).split("\n") if f],
        "stop": [],
        "reload": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Stable Diffusion Comfy", "download_model": True}).split("\n") if f],
    }
    extra_sd_comfy_enable: bool = False
    add_sd_comfy_enable: bool = False
    extra_sd_comfy_update: bool = False
    extra_sd_comfy_required_env_vars: List[str] = [""]
    extra_sd_comfy_args: str = ""

    def _add_sd_comfy(self, add=False):
        condition = self.add_sd_comfy_enable if add else self.extra_sd_comfy_enable
        if condition:
            self._add_script("sd_comfy")
            self._add_t2i_models()
            self._environment_variables['EXTRA_SD_COMFY_ARGS'] = self.extra_sd_comfy_args
            if self.extra_sd_comfy_update:
                set_value(self, "SD_COMFY_UPDATE_REPO", "auto", "")

    #### Stable Diffusion Fooocus ####
    sd_fooocus_action_in_progress: bool = False
    sd_fooocus_action_progress: str = ""
    sd_fooocus_action_log: str = ""
    sd_fooocus_view_log: bool = False
    sd_fooocus_substage: Dict[str, List[str]] = {
        "start": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Stable Diffusion Fooocus", "download_model": True}).split("\n") if f],
        "stop": [],
        "reload": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Stable Diffusion Fooocus", "download_model": True}).split("\n") if f],
    }
    extra_sd_fooocus_enable: bool = False
    add_sd_fooocus_enable: bool = False
    extra_sd_fooocus_update: bool = False
    extra_sd_fooocus_required_env_vars: List[str] = [""]
    extra_sd_fooocus_args: str = ""

    def _add_sd_fooocus(self, add=False):
        condition = self.add_sd_fooocus_enable if add else self.extra_sd_fooocus_enable
        if condition:
            self._add_script("sd_fooocus")
            self._add_t2i_models()
            self._environment_variables['EXTRA_SD_FOOOCUS_ARGS'] = self.extra_sd_fooocus_args
            if self.extra_sd_fooocus_update:
                set_value(self, "SD_FOOOCUS_UPDATE_REPO", "auto", "")
                
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
    extra_minio_required_env_vars: List[str] = [
        "extra_minio_host", "extra_minio_access_key", "extra_minio_secret_key"]

    def _check_env_minio(self, add=False):
        return check_env(self,
                         self.add_minio_enable if add else self.extra_minio_enable,
                         self.extra_minio_required_env_vars
                         )

    def _add_minio(self, add=False):
        condition = self.add_minio_enable if add else self.extra_minio_enable
        if condition:
            self._add_script("minio")
            self._environment_variables['S3_HOST_URL'] = self.extra_minio_host
            self._environment_variables['S3_ACCESS_KEY'] = self.extra_minio_access_key
            self._environment_variables['S3_SECRET_KEY'] = self.extra_minio_secret_key
            set_value(self, 'S3_MIRROR_PATH', self.extra_minio_mirror_path, "")
            set_value(self, 'S3_MIRROR_TO_BUCKET',
                      self.extra_minio_mirror_bucket, "")

    #### FastChat ###
    fastchat_action_in_progress: bool = False
    fastchat_action_progress: str = ""
    fastchat_action_log: str = ""
    fastchat_view_log: bool = False
    fastchat_substage: Dict[str, List[str]] = {
        "start": [f for f in STAGE_BASE_TEMPLATE.render({'title': "FastChat", "download_model": True}).split("\n") if f],
        "stop": [],
        "reload": [f for f in STAGE_BASE_TEMPLATE.render({'title': "FastChat", "download_model": True}).split("\n") if f],
    }
    add_fastchat_enable: bool = False
    extra_fastchat_enable: bool = False
    extra_fastchat_models: Dict[str, bool] = {
        model: False for model in FASTCHAT_MODELS}

    def update_fastchat_model_selecion(self, args: Dict[str, str]):
        update_checkbox_selecion(self.extra_fastchat_models, args)

    def _add_fastchat(self, add=False):
        condition = self.add_fastchat_enable if add else self.extra_fastchat_enable
        if condition:
            self._add_script("fastchat")
            self._environment_variables['FASTCHAT_MODEL'] = ",".join(
                [model for model, cond in self.extra_fastchat_models.items() if cond])

    #### TextGen ####
    textgen_action_in_progress: bool = False
    textgen_action_progress: str = ""
    textgen_action_log: str = ""
    textgen_view_log: bool = False
    textgen_substage: Dict[str, List[str]] = {
        "start": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Text generation Webui", "download_model": True}).split("\n") if f],
        "stop": [],
        "reload": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Text generation Webui", "download_model": True}).split("\n") if f],
    }
    add_textgen_enable: bool = False
    extra_textgen_enable: bool = False
    extra_textgen_update: bool = False
    extra_textgen_openai_api_enable: bool = False
    extra_textgen_api_model: Dict[str, bool] = {
        model: False for model in LLM_MODELS
    }
    extra_textgen_args: str = ""

    def _check_env_textgen(self, add=False):
        if self.extra_textgen_openai_api_enable:
            if not any(self.extra_textgen_api_model.values()):
                return [self.extra_textgen_api_model]
        return []

    def _add_textgen(self, add=False):
        condition = self.add_textgen_enable if add else self.extra_textgen_enable
        if condition:
            self._add_script("textgen")
            if self.extra_textgen_update:
                set_value(self, "TEXTGEN_UPDATE_REPO", "auto", "")
            if self.extra_textgen_openai_api_enable:
                self._environment_variables['TEXTGEN_ENABLE_OPENAI_API'] = "1"
                for model, cond in self.extra_textgen_api_model.items():
                    if cond:
                        self._environment_variables['TEXTGEN_OPENAI_MODEL'] = \
                            LLM_MAPPING[model].replace('/', '_')
                        self.extra_llm_models[model] = True
                        break
            self._add_llm_models()
            self._environment_variables['EXTRA_TEXTGEN_ARGS'] = self.extra_textgen_args

    #### LLM Model ####
    extra_llm_models: Dict[str, bool] = {model: False for model in LLM_MODELS}

    def _add_llm_models(self):
        self._environment_variables['LLM_MODEL_TO_DOWNLOAD'] = ",".join(
            [LLM_MAPPING[model] for model, cond in self.extra_llm_models.items() if cond])

    ### Command Server ####
    extra_command_enable: bool = False
    command_url: str = ""
    extra_command_user: str = ""
    extra_command_password: str = ""
    extra_command_required_env_vars: List[str] = [
        "extra_command_user", "extra_command_password"]

    def _check_env_command(self, add=False):
        return check_env(self, self.extra_command_enable, self.extra_command_required_env_vars)

    def _add_command(self, add=False):
        if self.extra_command_enable:
            self._add_script("command")
            self._environment_variables['COMMAND_USERNAME'] = self.extra_command_user
            self._environment_variables['COMMAND_PASSWORD'] = self.extra_command_password

    ### Image Browser ####
    image_browser_action_in_progress: bool = False
    image_browser_action_progress: str = ""
    image_browser_action_log: str = ""
    image_browser_view_log: bool = False
    image_browser_substage: Dict[str, List[str]] = {
        "start": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Image Browser", "download_model": False}).split("\n") if f],
        "stop": [],
        "reload": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Image Browser", "download_model": False}).split("\n") if f],
    }
    extra_image_browser_enable: bool = False
    add_image_browser_enable: bool = False
    extra_image_browser_key: str = ""
    extra_image_browser_required_env_vars: List[str] = [
        "extra_image_browser_key"]

    def _check_env_image_browser(self, add=False):
        return check_env(self,
                         self.add_image_browser_enable if add else self.extra_image_browser_enable,
                         self.extra_image_browser_required_env_vars
                         )

    def _add_image_browser(self, add=False):
        condition = self.add_image_browser_enable if add else self.extra_image_browser_enable
        if condition:
            self._add_script("image_browser")
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
    # extra_{{ name }}_enable: bool = False
    # add_{{ name }}_enable: bool = False
    # extra_{{ name }}_required_env_vars: List[str] = [""]

    # def _check_env_{{ name }}(self, add=False):
    #     return check_env(
    #         self,
    #         self.add_{{ name }}_enable if add else self.extra_{{ name }}_enable,
    #         self.extra_{{ name }}_required_env_vars
    #     )

    # def _add_{{ name }}(self, add=False):
    #     condition = self.add_{{ name }}_enable if add else self.extra_{{ name }}_enable
    #     if condition:
    #         self._add_script("{{ name }}")

    ### Flowise ####
    flowise_action_in_progress: bool = False
    flowise_action_progress: str = ""
    flowise_action_log: str = ""
    flowise_view_log: bool = False
    flowise_substage: Dict[str, List[str]] = {
        "start": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Flowise", "download_model": False}).split("\n") if f],
        "stop": [],
        "reload": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Flowise", "download_model": False}).split("\n") if f],
    }
    extra_flowise_enable: bool = False
    add_flowise_enable: bool = False
    extra_flowise_username: str = ""
    extra_flowise_password: str = ""
    extra_flowise_required_env_vars: List[str] = [
        "extra_flowise_username", "extra_flowise_password"
    ]

    def _check_env_flowise(self, add=False):
        return check_env(
            self,
            self.add_flowise_enable if add else self.extra_flowise_enable,
            self.extra_flowise_required_env_vars
        )

    def _add_flowise(self, add=False):
        condition = self.add_flowise_enable if add else self.extra_flowise_enable
        if condition:
            self._add_script("flowise")
            self._environment_variables['FLOWISE_USERNAME'] = self.extra_flowise_username
            self._environment_variables['FLOWISE_PASSWORD'] = self.extra_flowise_password

    ### Langflow ####
    langflow_action_in_progress: bool = False
    langflow_action_progress: str = ""
    langflow_action_log: str = ""
    langflow_view_log: bool = False
    langflow_substage: Dict[str, List[str]] = {
        "start": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Langflow", "download_model": False}).split("\n") if f],
        "stop": [],
        "reload": [f for f in STAGE_BASE_TEMPLATE.render({'title': "Langflow", "download_model": False}).split("\n") if f],
    }
    extra_langflow_enable: bool = False
    add_langflow_enable: bool = False
    extra_langflow_args: str = ""

    def _add_langflow(self, add=False):
        condition = self.add_langflow_enable if add else self.extra_langflow_enable
        if condition:
            self._add_script("langflow")
            self._environment_variables['EXTRA_LANGFLOW_ARGS'] = self.extra_langflow_args

    ### MusicGen ####
    musicgen_action_in_progress: bool = False
    musicgen_action_progress: str = ""
    musicgen_action_log: str = ""
    musicgen_view_log: bool = False
    musicgen_substage: Dict[str, List[str]] = {
        "start": [f for f in STAGE_BASE_TEMPLATE.render({'title': "{{ title }}", "download_model" : False}).split("\n") if f],
        "stop": [],
        "reload": [f for f in STAGE_BASE_TEMPLATE.render({'title': "{{ title }}", "download_model" : False}).split("\n") if f],
    }
    extra_musicgen_enable: bool = False
    add_musicgen_enable: bool = False
    extra_musicgen_update: bool = False
    extra_musicgen_required_env_vars: List[str] = [""]

    def _add_musicgen(self, add=False):
        condition = self.add_musicgen_enable if add else self.extra_musicgen_enable
        if condition:
            self._add_script("musicgen")
        if self.extra_musicgen_update:
            set_value(self, "MUSICGEN_UPDATE_REPO", "auto", "")
            
            
    ### Kosmos-2 ####
    kosmos2_action_in_progress: bool = False
    kosmos2_action_progress: str = ""
    kosmos2_action_log: str = ""
    kosmos2_view_log: bool = False
    kosmos2_substage: Dict[str, List[str]] = {
        "start": [f for f in STAGE_BASE_TEMPLATE.render({'title': "{{ title }}", "download_model" : True}).split("\n") if f],
        "stop": [],
        "reload": [f for f in STAGE_BASE_TEMPLATE.render({'title': "{{ title }}", "download_model" : True}).split("\n") if f],
    }
    extra_kosmos2_enable: bool = False
    add_kosmos2_enable: bool = False
    extra_kosmos2_required_env_vars: List[str] = [""]

    def _add_kosmos2(self, add=False):
        condition = self.add_kosmos2_enable if add else self.extra_kosmos2_enable
        if condition:
            self._add_script("kosmos2")
            
    ### Preprocess ####
    preprocess_action_in_progress: bool = False
    preprocess_action_progress: str = ""
    preprocess_action_log: str = ""
    preprocess_view_log: bool = False
    preprocess_substage: Dict[str, List[str]] = {
        "start": [f for f in STAGE_BASE_TEMPLATE.render({'title': "{{ title }}", "download_model" : False}).split("\n") if f],
        "stop": [],
        "reload": [f for f in STAGE_BASE_TEMPLATE.render({'title': "{{ title }}", "download_model" : False}).split("\n") if f],
    }
    extra_preprocess_enable: bool = False
    add_preprocess_enable: bool = False
    extra_preprocess_required_env_vars: List[str] = [""]

    def _add_preprocess(self, add=False):
        condition = self.add_preprocess_enable if add else self.extra_preprocess_enable
        if condition:
            self._add_script("preprocess")
            self._add_t2i_models()