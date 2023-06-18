from app.utils.components import *
from app.utils.constants import *
from app.utils.functions import *
from app.state.paperspace import EnvState
from app.state.paperspace_extra import ToolState
from app.state.control_panel import ControlPanelState
import pynecone as pc

def progress_log_panel(name: str) -> pc.component:
    progress_text = getattr(ControlPanelState, f"{name}_action_progress")
    progress_log = getattr(ControlPanelState, f"{name}_action_log")
    output = wrap_card(
        pc.text(progress_text, id=f"{name}_progress_text", class_name="pb-3",size="sm"),
        custom_code_block(progress_log, id=f"{name}_progress_log"),
        width="90%",
        add_cls="pt-2",
    )
    return output

def component_action_panel(name: str) -> pc.component:
    view_log = getattr(ControlPanelState, f"{name}_view_log")
    progress_log = getattr(ControlPanelState, f"{name}_action_log")
    return el.div(
        pc.cond(
            view_log,
            wrap_card(
                custom_code_block(progress_log),
                add_cls= "pt-2",
                width="90%",
            )
        ),
        wrap_row(
            pc.button(
                "Reload",
                # bg="yellow.600",
                class_name=BUTTON_CLS,
                size="md",
                on_click=[
                    lambda: EnvState.set_action_status(name, True),
                    lambda: ControlPanelState.component_action(name, "reload", get_ref_value_fn(prefix="control_panel")),
                ],
            ),
            pc.button(
                "Start",
                # bg="blue.600",
                class_name=BUTTON_CLS,
                size="md",
                on_click=[
                    lambda: EnvState.set_action_status(name, True),
                    lambda: ControlPanelState.component_action(name, "start", get_ref_value_fn(prefix="control_panel")),
                ]
            ),
            pc.button(
                "Stop",
                # bg="red.600",
                class_name=BUTTON_CLS,
                size="md",
                on_click=[
                    lambda: EnvState.set_action_status(name, True),
                    lambda: ControlPanelState.component_action(name, "stop", get_ref_value_fn(prefix="control_panel")),
                ]
            ),
            pc.button(
                "Check Status",
                # bg="red.600",
                class_name=BUTTON_CLS,
                size="md",
                on_click=[
                    lambda: EnvState.set_action_status(name, True),
                    lambda: ControlPanelState.check_process_status(name),
                ]
            ),
            specialButton(
                "View Log",
                # bg="red.600",
                class_name=BUTTON_CLS,
                size="md",
                # on_click= lambda condition: ControlPanelState.set_view_log(name),
                special_on_click=[
                    f"{view_log.full_name} = !{view_log.full_name}",
                    "setBase_state({...base_state})"
                ]
            ),
            add_cls = "pt-5",
            #wrap="wrap",      
            spacing="1em",
        ) 
    )



def extra_cloudflare(add=False) -> pc.component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return  pc.accordion_item(
                pc.accordion_button(
                    pc.text("Cloudflare Tunnel"),
                    pc.accordion_icon(),
                    class_name = ACCORDION_BUTTON_CLS,
                ),
                pc.accordion_panel(
                    wrap_row(
                        pc.checkbox("Enable", 
                            id = f"{prefix}add_cloudflared_enable" if add else f"{prefix}extra_cloudflared_enable",
                            class_name=add_class_tag(TEXT_COLOR_CLASS, "text-sm"),
                        ), 
                    ),
                    wrap_row(
                        component_with_title("Token",
                            pc.input,
                            input_kwargs={"id": f"{prefix}extra_cloudflared_token"},
                            vstack_kwargs={"align_items": "start"}
                        ),
                    ),    
                    pc.cond(
                        add,
                        pc.cond(
                            EnvState.cloudflared_action_in_progress,
                            progress_log_panel("cloudflared"),
                            component_action_panel("cloudflared"),
                        ),                         
                    ),      
                    class_name = "overflow-y-auto w-full"                  
                ),
            )
    
def extra_discord(add=False) -> pc.component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return  pc.accordion_item(
                pc.accordion_button(
                    pc.text("Discord Notification"),
                    pc.accordion_icon(),
                    class_name = ACCORDION_BUTTON_CLS,
                ),
                pc.accordion_panel(
                    wrap_row(
                        component_with_title("Webhook URL",
                            pc.text_area,
                            input_kwargs={"id": f"{prefix}extra_discord_token"},
                            vstack_kwargs={"class_name": "w-full", "align_items": "start"}
                        ),  
                    ),
                    class_name = "overflow-y-auto w-full"
                )
        )

def extra_rclone(add=False) -> pc.component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return  pc.accordion_item(
                pc.accordion_button(
                    pc.text("Remote File Explorer"),
                    pc.accordion_icon(),
                    class_name = ACCORDION_BUTTON_CLS,
                ),
                pc.accordion_panel(
                    wrap_row(
                        pc.checkbox("Enable", 
                            id = f"{prefix}add_rclone_enable" if add else f"{prefix}extra_rclone_enable",
                            class_name=add_class_tag(TEXT_COLOR_CLASS, "text-sm d-flex align-items-center"),
                        ), 
                    ),
                    wrap_row(
                        component_with_title("Username",
                            pc.input,
                            input_kwargs={"id": f"{prefix}extra_rclone_username"},
                            vstack_kwargs={"align_items": "start"}
                        ),
                        component_with_title("Password",
                            pc.input,
                            input_kwargs={"id": f"{prefix}extra_rclone_password"},
                            vstack_kwargs={"align_items": "start"}
                        ),                                         
                        add_cls="w-full", 
                        #wrap="wrap",
                        spacing="1em",
                    ),    
                    component_with_title("Local path (Optional)",
                        pc.input,
                        input_kwargs={"id": f"{prefix}extra_rclone_serve_path"},
                        vstack_kwargs={"class_name": "w-full", "align_items": "start"}
                    ),      
                    pc.cond(
                        add,
                        pc.cond(
                            EnvState.rclone_action_in_progress,
                            progress_log_panel("rclone"),
                            component_action_panel("rclone"),
                        ),                         
                    ),
                    class_name = "overflow-y-auto w-full"
                ),
        )

def prepare_t2i_model_selection(add=False) -> pc.component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return pc.accordion_item(
                pc.accordion_button(
                    pc.text("Model Selection"),
                    pc.accordion_icon(),
                    class_name = ACCORDION_BUTTON_CLS,
                ),
                pc.accordion_panel(
                    pc.text("Reload Stable Diffusion service to update the model selection",
                            class_name=add_class_tag(TEXT_COLOR_CLASS, "italic pb-2"),
                            ),
                    component_with_title("HuggingFace Token (Optional)",
                        pc.input,
                        input_kwargs={"id": f"{prefix}extra_t2i_hf_token"},
                        vstack_kwargs={"class_name": "w-full", "align_items": "start"}
                    ), 
                    component_with_title("Model List",
                        pc.text_area,
                        input_kwargs={"id": f"{prefix}extra_t2i_model_list"},
                        vstack_kwargs={"class_name": "w-full", "align_items": "start"}
                    ),  
                    component_with_title("VAE List",
                        pc.text_area,
                        input_kwargs={"id": f"{prefix}extra_t2i_vae_list"},
                        vstack_kwargs={"class_name": "w-full", "align_items": "start"}
                    ),  
                    component_with_title("Embedding List",
                        pc.text_area,
                        input_kwargs={"id": f"{prefix}extra_t2i_embedding_list"},
                        vstack_kwargs={"class_name": "w-full", "align_items": "start"}
                    ),  
                    component_with_title("Lora List",
                        pc.text_area,
                        input_kwargs={"id": f"{prefix}extra_t2i_lora_list"},
                        vstack_kwargs={"class_name": "w-full", "align_items": "start"}
                    ),  
                    component_with_title("Controlnet List",
                        pc.text_area,
                        input_kwargs={"id": f"{prefix}extra_t2i_controlnet_list"},
                        vstack_kwargs={"class_name": "w-full", "align_items": "start"}
                    ),
                    class_name = "overflow-y-auto w-full"
                )
    )
    
def extra_sd_webui(add=False) -> pc.component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return  pc.accordion_item(
                pc.accordion_button(
                    pc.text("Stable Diffusion WebUI"),
                    pc.accordion_icon(),
                    class_name = ACCORDION_BUTTON_CLS,
                ),
                pc.accordion_panel(
                    wrap_row(
                        pc.checkbox("Enable", 
                            id = f"{prefix}add_sd_webui_enable" if add else f"{prefix}extra_sd_webui_enable",
                            class_name=add_class_tag(TEXT_COLOR_CLASS, "text-sm"),
                        ), 
                    ),
                    wrap_row(
                        pc.checkbox("Update to latest", 
                            id = f"{prefix}extra_sd_webui_update",
                            class_name=add_class_tag(TEXT_COLOR_CLASS, "text-sm"),
                        ), 
                        pc.checkbox("Enable Xformers", 
                            id = f"{prefix}extra_sd_webui_xformers" ,
                            class_name=add_class_tag(TEXT_COLOR_CLASS, "text-sm"),
                        ), 
                    ),
                    wrap_row(
                        component_with_title("Gradio Auth (Username:Password)",
                            pc.input,
                            input_kwargs={"id": f"{prefix}extra_sd_webui_auth"},
                            vstack_kwargs={"align_items": "start"}
                        ),                
                        #wrap="wrap",
                        # spacing="1em"
                    ),
                    pc.cond(
                        add,
                        pc.cond(
                            EnvState.sd_webui_action_in_progress,
                            progress_log_panel("sd_webui"),
                            component_action_panel("sd_webui"),
                        ),                         
                    ),       
                    class_name = "overflow-y-auto w-full"      
                ),
            ) 

def extra_sd_volta(add=False) -> pc.Component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return  pc.accordion_item(
                pc.accordion_button(
                    pc.text("Stable Diffusion Volta"),
                    pc.accordion_icon(),
                    class_name = ACCORDION_BUTTON_CLS,
                ),
                pc.accordion_panel(
                    wrap_row(
                        pc.checkbox("Enable", 
                            id = f"{prefix}add_sd_volta_enable" if add else f"{prefix}extra_sd_volta_enable",
                            class_name=add_class_tag(TEXT_COLOR_CLASS, "text-sm"),
                        ),             
                        #wrap="wrap",
                        # spacing="1em",
                    ),
                    wrap_row(
                        pc.checkbox("Update to latest", 
                            id = f"{prefix}extra_sd_volta_update",
                            class_name=add_class_tag(TEXT_COLOR_CLASS, "text-sm"),
                        ),  
                    ),
                    pc.cond(
                        add,
                        pc.cond(
                            EnvState.sd_volta_action_in_progress,
                            progress_log_panel("sd_volta"),
                            component_action_panel("sd_volta"),
                        ),                         
                    ),          
                    class_name = "overflow-y-auto w-full"   
                ),
            ) 
    
def extra_sd_comfy(add=False) -> pc.Component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return  pc.accordion_item(
                pc.accordion_button(
                    pc.text("Stable Diffusion Comfy"),
                    pc.accordion_icon(),
                    class_name = ACCORDION_BUTTON_CLS,
                ),
                pc.accordion_panel(
                    wrap_row(
                        pc.checkbox("Enable", 
                            id = f"{prefix}add_sd_comfy_enable" if add else f"{prefix}extra_sd_comfy_enable",
                            class_name=add_class_tag(TEXT_COLOR_CLASS, "text-sm"),
                        ),             
                        #wrap="wrap",
                        # spacing="1em",
                    ),
                    wrap_row(
                        pc.checkbox("Update to latest", 
                            id = f"{prefix}extra_sd_comfy_update",
                            class_name=add_class_tag(TEXT_COLOR_CLASS, "text-sm"),
                        ),  
                    ),
                    pc.cond(
                        add,
                        pc.cond(
                            EnvState.sd_comfy_action_in_progress,
                            progress_log_panel("sd_comfy"),
                            component_action_panel("sd_comfy"),
                        ),                         
                    ),          
                    class_name = "overflow-y-auto w-full"   
                ),
            ) 

def extra_t2i_image_browser(add=False) -> pc.Component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return  pc.accordion_item(
                pc.accordion_button(
                    pc.text("Image Browser"),
                    pc.accordion_icon(),
                    class_name = ACCORDION_BUTTON_CLS,
                ),
                pc.accordion_panel(
                    wrap_row(
                        pc.checkbox("Enable", 
                            id = f"{prefix}add_image_browser_enable" if add else f"{prefix}extra_image_browser_enable",
                            class_name=add_class_tag(TEXT_COLOR_CLASS, "text-sm"),
                        ),             
                        #wrap="wrap",
                        # spacing="1em",
                    ),
                    wrap_row(
                        component_with_title("Secret key",
                            pc.input,
                            input_kwargs={"id": f"{prefix}extra_image_browser_key"},
                            vstack_kwargs={"align_items": "start"}
                        ),
                    ),
                    pc.cond(
                        add,
                        pc.cond(
                            EnvState.image_browser_action_in_progress,
                            progress_log_panel("image_browser"),
                            component_action_panel("image_browser"),
                        ),                         
                    ),          
                    class_name = "overflow-y-auto w-full"   
                ),
            ) 

def extra_minio(add=False) -> pc.component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return  pc.accordion_item(
                pc.accordion_button(
                    pc.text("Minio"),
                    pc.accordion_icon(),
                    class_name = ACCORDION_BUTTON_CLS,
                ),
                pc.accordion_panel(
                    wrap_row(
                        pc.checkbox("Enable", 
                            id = f"{prefix}add_minio_enable" if add else f"{prefix}extra_minio_enable",
                            class_name=add_class_tag(TEXT_COLOR_CLASS, "text-sm"),
                        ), 
                    ),     
                    component_with_title("S3 Host URL",
                        pc.input,
                        input_kwargs={"id": f"{prefix}extra_minio_host"},
                        vstack_kwargs={"class_name": "w-full", "align_items": "start"}
                    ),
                    wrap_row(
                        component_with_title("S3 Access Key",
                            pc.input,
                            input_kwargs={"id": f"{prefix}extra_minio_access_key"},
                            vstack_kwargs={"align_items": "start"}
                        ),
                        component_with_title("S3 Secret Key",
                            pc.input,
                            input_kwargs={"id": f"{prefix}extra_minio_secret_key"},
                            vstack_kwargs={"align_items": "start"}
                        ),
                        #wrap="wrap",
                        spacing="1em",
                    ),
                    wrap_row(
                        component_with_title("Local path to mirror to S3(Optional)",
                            pc.input,
                            input_kwargs={"id": f"{prefix}extra_minio_mirror_path"},
                            vstack_kwargs={"align_items": "start"}
                        ),
                        component_with_title("S3 target path(Optional)",
                            pc.input,
                            input_kwargs={"id": f"{prefix}extra_minio_mirror_bucket"},
                            vstack_kwargs={"align_items": "start"}
                        ),    
                        #wrap="wrap",
                        spacing="1em",
                    ),
                        pc.cond(
                            add,
                            pc.cond(
                                EnvState.minio_action_in_progress,
                                progress_log_panel("minio"),
                                component_action_panel("minio"),
                            ),                         
                         ),   
                         class_name = "overflow-y-auto w-full"                    
                    ),
        )
      
def extra_command(add=False) -> pc.component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return  pc.accordion_item(
                pc.accordion_button(
                    pc.text("Command Server"),
                    pc.accordion_icon(),
                    class_name = ACCORDION_BUTTON_CLS,
                ),
                pc.accordion_panel(
                    wrap_row(
                        pc.checkbox("Enable", 
                            id = f"{prefix}extra_command_enable",
                            class_name=add_class_tag(TEXT_COLOR_CLASS, "text-sm"),
                        ),
                    ),
                    wrap_row(
                        component_with_title("Server URL",
                            pc.input,
                            input_kwargs={"id": f"{prefix}extra_command_url"},
                            vstack_kwargs={"align_items": "start"}
                        ),
                        component_with_title("Username",
                            pc.input,
                            input_kwargs={"id": f"{prefix}extra_command_user"},
                            vstack_kwargs={"align_items": "start"}
                        ),
                        component_with_title("Password",
                            pc.input,
                            input_kwargs={"id": f"{prefix}extra_command_password"},
                            vstack_kwargs={ "align_items": "start"}
                        ),
                        #wrap="wrap",
                        spacing="1em",
                        align_items="stretch",
                    ),      
                    class_name = "overflow-y-auto w-full"
                ),
        )
    
def extra_fastchat(add=False) -> pc.component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return  pc.accordion_item(
                pc.accordion_button(
                    pc.text("Fastchat"),
                    pc.accordion_icon(),
                    class_name = ACCORDION_BUTTON_CLS,
                ),
                pc.accordion_panel(
                    wrap_row(
                        pc.checkbox("Enable", 
                            id = f"{prefix}add_fastchat_enable" if add else f"{prefix}extra_fastchat_enable",
                            class_name=add_class_tag(TEXT_COLOR_CLASS, "text-sm d-flex align-items-center"),
                        ), 
                        add_cls="w-full" 
                    ), 
                    wrap_row(
                        pc.text(
                            "Models", 
                            class_name=add_class_tag(TEXT_COLOR_CLASS, "text-sm")
                        ),
                    ),   
                    pc.wrap(
                        *[
                            pc.checkbox(
                                model,
                                id=f"{prefix}extra_fastchat_models__{idx}",
                                class_name=add_class_tag(TEXT_COLOR_CLASS, "text-sm d-flex align-items-center"),
                            ) for idx, model in enumerate(FASTCHAT_MODELS)
                        ],
                        spacing="30px",
                        justify="start",
                        align_items="start"
                    ),
                    pc.cond(
                        add,
                        pc.cond(
                            EnvState.fastchat_action_in_progress,
                            progress_log_panel("fastchat"),
                            component_action_panel("fastchat"),
                        ),                         
                    ),   
                    class_name = "overflow-y-auto w-full"                    
                ),
        )
    
def extra_textgen(add=False) -> pc.component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return  pc.accordion_item(
                pc.accordion_button(
                    pc.text("Text Generation WebUI"),
                    pc.accordion_icon(),
                    class_name = ACCORDION_BUTTON_CLS,
                ),
                pc.accordion_panel(
                    wrap_row(
                        pc.checkbox("Enable", 
                            id = f"{prefix}add_textgen_enable" if add else f"{prefix}extra_textgen_enable",
                            class_name=add_class_tag(TEXT_COLOR_CLASS, "text-sm d-flex align-items-center"),
                        ), 
                        add_cls="w-full" 
                    ), 
                    wrap_row(
                        pc.text(
                            "Models", 
                            class_name=add_class_tag(TEXT_COLOR_CLASS, "text-sm")
                        ),
                    ),    
                    pc.wrap(
                        *[
                            pc.checkbox(
                                model,
                                id=f"{prefix}extra_textgen_models__{idx}",
                                class_name=add_class_tag(TEXT_COLOR_CLASS, "text-sm d-flex align-items-center"),
                            ) for idx, model in enumerate(TEXTGEN_MODELS)
                        ],
                        spacing="30px",
                        justify="start",
                        align_items="start"
                    ),
                    pc.cond(
                        add,
                        pc.cond(
                            EnvState.textgen_action_in_progress,
                            progress_log_panel("textgen"),
                            component_action_panel("textgen"),
                        ),                         
                    ),     
                    class_name = "overflow-y-auto w-full"                  
                ),
        )