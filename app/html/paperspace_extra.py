from app.utils.components import *
from app.utils.constants import *
from app.utils.functions import *
from app.state.paperspace import EnvState
from app.state.paperspace_extra import ToolState
from app.state.control_panel import ControlPanelState
import reflex as rx


def progress_log_panel(name: str) -> rx.component:
    progress_text = getattr(ControlPanelState, f"{name}_action_progress")
    progress_log = getattr(ControlPanelState, f"{name}_action_log")
    output = wrap_card(
        rx.text(progress_text,
                id=f"{name}_progress_text", class_name="pb-3", size="sm"),
        custom_code_block(progress_log, id=f"{name}_progress_log"),
        width="90%",
        add_cls="pt-2",
    )
    return output


def download_action_panel(name: str) -> rx.component:
    return el.div(
        rx.cond(
            ControlPanelState.task_progress[name] != "",
            wrap_card(
                custom_code_block(ControlPanelState.task_progress[name]),
                add_cls="pt-2",
                width="90%",
            )
        ),
        wrap_row(
            rx.cond(
                ControlPanelState.task_in_progress[name],
                rx.circular_progress(is_indeterminate=True),
                rx.button(
                    "Download",
                    # bg="blue.600",
                    class_name=BUTTON_CLS,
                    size="md",
                    on_click=[
                        lambda: ControlPanelState.set_task_in_progress(name),
                        lambda: ControlPanelState.download_model(
                            name, get_ref_value_fn(prefix="control_panel")),
                    ]
                ),
            ),
            add_cls="pt-5",
            # wrap="wrap",
            spacing="1em",
        )
    )


def component_action_panel(name: str) -> rx.component:
    view_log = getattr(ControlPanelState, f"{name}_view_log")
    progress_log = getattr(ControlPanelState, f"{name}_action_log")
    return el.div(
        rx.cond(
            view_log,
            wrap_card(
                custom_code_block(progress_log),
                add_cls="pt-2",
                width="90%",
            )
        ),
        wrap_row(
            rx.button(
                "Reload",
                # bg="yellow.600",
                class_name=BUTTON_CLS,
                size="md",
                on_click=[
                    lambda: EnvState.set_action_status(name, True),
                    lambda: ControlPanelState.component_action(
                        name, "reload", get_ref_value_fn(prefix="control_panel")),
                ],
            ),
            rx.button(
                "Start",
                # bg="blue.600",
                class_name=BUTTON_CLS,
                size="md",
                on_click=[
                    lambda: EnvState.set_action_status(name, True),
                    lambda: ControlPanelState.component_action(
                        name, "start", get_ref_value_fn(prefix="control_panel")),
                ]
            ),
            rx.button(
                "Stop",
                # bg="red.600",
                class_name=BUTTON_CLS,
                size="md",
                on_click=[
                    lambda: EnvState.set_action_status(name, True),
                    lambda: ControlPanelState.component_action(
                        name, "stop", get_ref_value_fn(prefix="control_panel")),
                ]
            ),
            rx.button(
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
            add_cls="pt-5",
            # wrap="wrap",
            spacing="1em",
        )
    )


def extra_cloudflare(add=False) -> rx.component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return rx.accordion_item(
        rx.accordion_button(
            rx.text("Cloudflare Tunnel"),
            rx.accordion_icon(),
            class_name=ACCORDION_BUTTON_CLS,
        ),
        rx.accordion_panel(
            wrap_row(
                rx.checkbox("Enable",
                            id=f"{prefix}add_cloudflared_enable" if add else f"{prefix}extra_cloudflared_enable",
                            class_name=add_class_tag(
                                TEXT_COLOR_CLASS, "text-sm"),
                            ),
            ),
            wrap_row(
                component_with_title("Token",
                                     rx.input,
                                     input_kwargs={
                                         "id": f"{prefix}extra_cloudflared_token"},
                                     vstack_kwargs={
                                         "align_items": "start"}
                                     ),
            ),
            rx.cond(
                add,
                rx.cond(
                    EnvState.cloudflared_action_in_progress,
                    progress_log_panel("cloudflared"),
                    component_action_panel("cloudflared"),
                ),
            ),
            class_name="overflow-y-auto w-full"
        ),
    )


def extra_discord(add=False) -> rx.component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return rx.accordion_item(
        rx.accordion_button(
            rx.text("Discord Notification"),
            rx.accordion_icon(),
            class_name=ACCORDION_BUTTON_CLS,
        ),
        rx.accordion_panel(
            wrap_row(
                component_with_title("Webhook URL",
                                     rx.text_area,
                                     input_kwargs={
                                         "id": f"{prefix}extra_discord_token"},
                                     vstack_kwargs={
                                         "class_name": "w-full", "align_items": "start"}
                                     ),
            ),
            class_name="overflow-y-auto w-full"
        )
    )


def extra_rclone(add=False) -> rx.component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return rx.accordion_item(
        rx.accordion_button(
            rx.text("Remote File Explorer"),
            rx.accordion_icon(),
            class_name=ACCORDION_BUTTON_CLS,
        ),
        rx.accordion_panel(
            wrap_row(
                rx.checkbox("Enable",
                            id=f"{prefix}add_rclone_enable" if add else f"{prefix}extra_rclone_enable",
                            class_name=add_class_tag(
                                TEXT_COLOR_CLASS, "text-sm d-flex align-items-center"),
                            ),
            ),
            wrap_row(
                component_with_title("Username",
                                     rx.input,
                                     input_kwargs={
                                         "id": f"{prefix}extra_rclone_username"},
                                     vstack_kwargs={
                                         "align_items": "start"}
                                     ),
                component_with_title("Password",
                                     rx.input,
                                     input_kwargs={
                                         "id": f"{prefix}extra_rclone_password"},
                                     vstack_kwargs={
                                         "align_items": "start"}
                                     ),
                add_cls="w-full",
                # wrap="wrap",
                        spacing="1em",
            ),
            component_with_title("Local path (Optional)",
                                 rx.input,
                                 input_kwargs={
                                     "id": f"{prefix}extra_rclone_serve_path"},
                                 vstack_kwargs={"class_name": "w-full",
                                                "align_items": "start"}
                                 ),
            rx.cond(
                add,
                rx.cond(
                    EnvState.rclone_action_in_progress,
                    progress_log_panel("rclone"),
                    component_action_panel("rclone"),
                ),
            ),
            class_name="overflow-y-auto w-full"
        ),
    )


def prepare_t2i_model_selection(add=False) -> rx.component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return rx.accordion_item(
        rx.accordion_button(
            rx.text("Stable Diffusion Model Downloader"),
            rx.accordion_icon(),
            class_name=ACCORDION_BUTTON_CLS,
        ),
        rx.accordion_panel(
            component_with_title("HuggingFace Token (Optional)",
                                 rx.input,
                                 input_kwargs={
                                     "id": f"{prefix}extra_t2i_hf_token"},
                                 vstack_kwargs={"class_name": "w-full",
                                                "align_items": "start"}
                                 ),
            component_with_title("Model List",
                                 rx.text_area,
                                 input_kwargs={
                                     "id": f"{prefix}extra_t2i_model_list"},
                                 vstack_kwargs={"class_name": "w-full",
                                                "align_items": "start"}
                                 ),
            component_with_title("VAE List",
                                 rx.text_area,
                                 input_kwargs={
                                     "id": f"{prefix}extra_t2i_vae_list"},
                                 vstack_kwargs={"class_name": "w-full",
                                                "align_items": "start"}
                                 ),
            component_with_title("Embedding List",
                                 rx.text_area,
                                 input_kwargs={
                                     "id": f"{prefix}extra_t2i_embedding_list"},
                                 vstack_kwargs={"class_name": "w-full",
                                                "align_items": "start"}
                                 ),
            component_with_title("Lora List",
                                 rx.text_area,
                                 input_kwargs={
                                     "id": f"{prefix}extra_t2i_lora_list"},
                                 vstack_kwargs={"class_name": "w-full",
                                                "align_items": "start"}
                                 ),
            component_with_title("Controlnet List",
                                 rx.text_area,
                                 input_kwargs={
                                     "id": f"{prefix}extra_t2i_controlnet_list"},
                                 vstack_kwargs={"class_name": "w-full",
                                                "align_items": "start"}
                                 ),
            rx.cond(
                add,
                download_action_panel("sd_download")
            ),
            class_name="overflow-y-auto w-full"
        )
    )


def extra_sd_webui(add=False) -> rx.component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return rx.accordion_item(
        rx.accordion_button(
            rx.text("Stable Diffusion WebUI"),
            rx.accordion_icon(),
            class_name=ACCORDION_BUTTON_CLS,
        ),
        rx.accordion_panel(
            wrap_row(
                rx.checkbox("Enable",
                            id=f"{prefix}add_sd_webui_enable" if add else f"{prefix}extra_sd_webui_enable",
                            class_name=add_class_tag(
                                TEXT_COLOR_CLASS, "text-sm"),
                            ),
            ),
            wrap_row(
                rx.checkbox("Update to latest",
                            id=f"{prefix}extra_sd_webui_update",
                            class_name=add_class_tag(
                                TEXT_COLOR_CLASS, "text-sm"),
                            ),
                rx.checkbox("Enable Xformers",
                            id=f"{prefix}extra_sd_webui_xformers",
                            class_name=add_class_tag(
                                TEXT_COLOR_CLASS, "text-sm"),
                            ),
            ),
            wrap_row(
                component_with_title("Gradio Auth (Username:Password)",
                                     rx.input,
                                     input_kwargs={
                                         "id": f"{prefix}extra_sd_webui_auth"},
                                     vstack_kwargs={
                                         "align_items": "start"}
                                     ),
                # wrap="wrap",
                # spacing="1em"
            ),
            rx.cond(
                add,
                rx.cond(
                    EnvState.sd_webui_action_in_progress,
                    progress_log_panel("sd_webui"),
                    component_action_panel("sd_webui"),
                ),
            ),
            class_name="overflow-y-auto w-full"
        ),
    )


def extra_sd_volta(add=False) -> rx.Component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return rx.accordion_item(
        rx.accordion_button(
            rx.text("Stable Diffusion Volta"),
            rx.accordion_icon(),
            class_name=ACCORDION_BUTTON_CLS,
        ),
        rx.accordion_panel(
            wrap_row(
                rx.checkbox("Enable",
                            id=f"{prefix}add_sd_volta_enable" if add else f"{prefix}extra_sd_volta_enable",
                            class_name=add_class_tag(
                                TEXT_COLOR_CLASS, "text-sm"),
                            ),
                # wrap="wrap",
                # spacing="1em",
            ),
            wrap_row(
                rx.checkbox("Update to latest",
                            id=f"{prefix}extra_sd_volta_update",
                            class_name=add_class_tag(
                                TEXT_COLOR_CLASS, "text-sm"),
                            ),
            ),
            rx.cond(
                add,
                rx.cond(
                    EnvState.sd_volta_action_in_progress,
                    progress_log_panel("sd_volta"),
                    component_action_panel("sd_volta"),
                ),
            ),
            class_name="overflow-y-auto w-full"
        ),
    )


def extra_sd_comfy(add=False) -> rx.Component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return rx.accordion_item(
        rx.accordion_button(
            rx.text("Stable Diffusion Comfy"),
            rx.accordion_icon(),
            class_name=ACCORDION_BUTTON_CLS,
        ),
        rx.accordion_panel(
            wrap_row(
                rx.checkbox("Enable",
                            id=f"{prefix}add_sd_comfy_enable" if add else f"{prefix}extra_sd_comfy_enable",
                            class_name=add_class_tag(
                                TEXT_COLOR_CLASS, "text-sm"),
                            ),
                # wrap="wrap",
                # spacing="1em",
            ),
            wrap_row(
                rx.checkbox("Update to latest",
                            id=f"{prefix}extra_sd_comfy_update",
                            class_name=add_class_tag(
                                TEXT_COLOR_CLASS, "text-sm"),
                            ),
            ),
            rx.cond(
                add,
                rx.cond(
                    EnvState.sd_comfy_action_in_progress,
                    progress_log_panel("sd_comfy"),
                    component_action_panel("sd_comfy"),
                ),
            ),
            class_name="overflow-y-auto w-full"
        ),
    )


def extra_t2i_image_browser(add=False) -> rx.Component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return rx.accordion_item(
        rx.accordion_button(
            rx.text("Image Browser"),
            rx.accordion_icon(),
            class_name=ACCORDION_BUTTON_CLS,
        ),
        rx.accordion_panel(
            wrap_row(
                rx.checkbox("Enable",
                            id=f"{prefix}add_image_browser_enable" if add else f"{prefix}extra_image_browser_enable",
                            class_name=add_class_tag(
                                TEXT_COLOR_CLASS, "text-sm"),
                            ),
                # wrap="wrap",
                # spacing="1em",
            ),
            wrap_row(
                component_with_title("Secret key",
                                     rx.input,
                                     input_kwargs={
                                         "id": f"{prefix}extra_image_browser_key"},
                                     vstack_kwargs={
                                         "align_items": "start"}
                                     ),
            ),
            rx.cond(
                add,
                rx.cond(
                    EnvState.image_browser_action_in_progress,
                    progress_log_panel("image_browser"),
                    component_action_panel("image_browser"),
                ),
            ),
            class_name="overflow-y-auto w-full"
        ),
    )


def extra_minio(add=False) -> rx.component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return rx.accordion_item(
        rx.accordion_button(
            rx.text("Minio"),
            rx.accordion_icon(),
            class_name=ACCORDION_BUTTON_CLS,
        ),
        rx.accordion_panel(
            wrap_row(
                rx.checkbox("Enable",
                            id=f"{prefix}add_minio_enable" if add else f"{prefix}extra_minio_enable",
                            class_name=add_class_tag(
                                TEXT_COLOR_CLASS, "text-sm"),
                            ),
            ),
            component_with_title("S3 Host URL",
                                 rx.input,
                                 input_kwargs={
                                     "id": f"{prefix}extra_minio_host"},
                                 vstack_kwargs={"class_name": "w-full",
                                                "align_items": "start"}
                                 ),
            wrap_row(
                component_with_title("S3 Access Key",
                                     rx.input,
                                     input_kwargs={
                                         "id": f"{prefix}extra_minio_access_key"},
                                     vstack_kwargs={
                                         "align_items": "start"}
                                     ),
                component_with_title("S3 Secret Key",
                                     rx.input,
                                     input_kwargs={
                                         "id": f"{prefix}extra_minio_secret_key"},
                                     vstack_kwargs={
                                         "align_items": "start"}
                                     ),
                # wrap="wrap",
                spacing="1em",
            ),
            wrap_row(
                component_with_title("Local path to mirror to S3(Optional)",
                                     rx.input,
                                     input_kwargs={
                                         "id": f"{prefix}extra_minio_mirror_path"},
                                     vstack_kwargs={
                                         "align_items": "start"}
                                     ),
                component_with_title("S3 target path(Optional)",
                                     rx.input,
                                     input_kwargs={
                                         "id": f"{prefix}extra_minio_mirror_bucket"},
                                     vstack_kwargs={
                                         "align_items": "start"}
                                     ),
                # wrap="wrap",
                spacing="1em",
            ),
            rx.cond(
                add,
                rx.cond(
                    EnvState.minio_action_in_progress,
                    progress_log_panel("minio"),
                    component_action_panel("minio"),
                ),
            ),
            class_name="overflow-y-auto w-full"
        ),
    )


def extra_command(add=False) -> rx.component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return rx.accordion_item(
        rx.accordion_button(
            rx.text("Command Server"),
            rx.accordion_icon(),
            class_name=ACCORDION_BUTTON_CLS,
        ),
        rx.accordion_panel(
            wrap_row(
                rx.checkbox("Enable",
                            id=f"{prefix}extra_command_enable",
                            class_name=add_class_tag(
                                TEXT_COLOR_CLASS, "text-sm"),
                            ),
            ),
            wrap_row(
                component_with_title("Server URL",
                                     rx.input,
                                     input_kwargs={
                                         "id": f"{prefix}extra_command_url"},
                                     vstack_kwargs={
                                         "align_items": "start"}
                                     ),
                component_with_title("Username",
                                     rx.input,
                                     input_kwargs={
                                         "id": f"{prefix}extra_command_user"},
                                     vstack_kwargs={
                                         "align_items": "start"}
                                     ),
                component_with_title("Password",
                                     rx.input,
                                     input_kwargs={
                                         "id": f"{prefix}extra_command_password"},
                                     vstack_kwargs={
                                         "align_items": "start"}
                                     ),
                # wrap="wrap",
                spacing="1em",
                align_items="stretch",
            ),
            class_name="overflow-y-auto w-full"
        ),
    )


def extra_fastchat(add=False) -> rx.component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return rx.accordion_item(
        rx.accordion_button(
            rx.text("Fastchat"),
            rx.accordion_icon(),
            class_name=ACCORDION_BUTTON_CLS,
        ),
        rx.accordion_panel(
            wrap_row(
                rx.checkbox("Enable",
                            id=f"{prefix}add_fastchat_enable" if add else f"{prefix}extra_fastchat_enable",
                            class_name=add_class_tag(
                                TEXT_COLOR_CLASS, "text-sm d-flex align-items-center"),
                            ),
                add_cls="w-full"
            ),
            wrap_row(
                rx.text(
                    "Models",
                    class_name=add_class_tag(
                        TEXT_COLOR_CLASS, "text-sm")
                ),
            ),
            rx.wrap(
                *[
                    rx.checkbox(
                        model,
                        id=f"{prefix}extra_fastchat_models__{idx}",
                        class_name=add_class_tag(
                            TEXT_COLOR_CLASS, "text-sm d-flex align-items-center"),
                    ) for idx, model in enumerate(FASTCHAT_MODELS)
                ],
                spacing="30px",
                justify="start",
                align_items="start"
            ),
            rx.cond(
                add,
                rx.cond(
                    EnvState.fastchat_action_in_progress,
                    progress_log_panel("fastchat"),
                    component_action_panel("fastchat"),
                ),
            ),
            class_name="overflow-y-auto w-full"
        ),
    )


def extra_enable_textgen_api(add=False) -> rx.component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return el.div(
        wrap_row(
            rx.checkbox("Enable OPENAI Style API",
                        id=f"{prefix}extra_textgen_openai_api_enable",
                        class_name=add_class_tag(
                            TEXT_COLOR_CLASS, "text-sm d-flex align-items-center"),
                        ),
        ),
        component_with_title(
            "Model",
            rx.radio_group,
            rx.hstack(
                *[
                    rx.radio(
                        model,
                        id=f"{prefix}extra_textgen_api_model__{idx}",
                    )
                    for idx, model in enumerate(LLM_MODELS)
                ],
                spacing="1em",
            ),
            vstack_kwargs={
                "align_items": "start"
            }
        )
    )


def extra_textgen(add=False) -> rx.component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return rx.accordion_item(
        rx.accordion_button(
            rx.text("Text Generation WebUI"),
            rx.accordion_icon(),
            class_name=ACCORDION_BUTTON_CLS,
        ),
        rx.accordion_panel(
            wrap_row(
                rx.checkbox("Enable",
                            id=f"{prefix}add_textgen_enable" if add else f"{prefix}extra_textgen_enable",
                            class_name=add_class_tag(
                                TEXT_COLOR_CLASS, "text-sm d-flex align-items-center"),
                            ),
                add_cls="w-full"
            ),
            extra_enable_textgen_api(add),
            rx.cond(
                add,
                rx.cond(
                    EnvState.textgen_action_in_progress,
                    progress_log_panel("textgen"),
                    component_action_panel("textgen"),
                ),
            ),
            class_name="overflow-y-auto w-full"
        ),
    )


def extra_llm_model_download(add=False) -> rx.component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return rx.accordion_item(
        rx.accordion_button(
            rx.text("LLM Model Download"),
            rx.accordion_icon(),
            class_name=ACCORDION_BUTTON_CLS,
        ),
        rx.accordion_panel(
            rx.wrap(
                *[
                    rx.checkbox(
                        model,
                        id=f"{prefix}extra_llm_models__{idx}",
                        class_name=add_class_tag(
                            TEXT_COLOR_CLASS, "text-sm d-flex align-items-center"),
                    ) for idx, model in enumerate(LLM_MODELS)
                ],
                spacing="30px",
                justify="start",
                align_items="start"
            ),
            rx.cond(
                add,
                download_action_panel("llm_download")
            ),
            class_name="overflow-y-auto w-full"
        ),
    )


def extra_flowise(add=False) -> rx.component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return rx.accordion_item(
        rx.accordion_button(
            rx.text("Flowise"),
            rx.accordion_icon(),
            class_name=ACCORDION_BUTTON_CLS,
        ),
        rx.accordion_panel(
            wrap_row(
                rx.checkbox("Enable",
                            id=f"{prefix}add_flowise_enable" if add else f"{prefix}extra_flowise_enable",
                            class_name=add_class_tag(
                                TEXT_COLOR_CLASS, "text-sm d-flex align-items-center"),
                            ),
                wrap_row(
                    component_with_title("Username",
                                         rx.input,
                                         input_kwargs={
                                             "id": f"{prefix}extra_flowise_user"},
                                         vstack_kwargs={
                                             "align_items": "start"}
                                         ),
                    component_with_title("Password",
                                         rx.input,
                                         input_kwargs={
                                             "id": f"{prefix}extra_flowise_password"},
                                         vstack_kwargs={
                                             "align_items": "start"}
                                         ),
                ),
                add_cls="w-full"
            ),
            rx.cond(
                add,
                rx.cond(
                    EnvState.flowise_action_in_progress,
                    progress_log_panel("flowise"),
                    component_action_panel("flowise"),
                ),
            ),
            class_name="overflow-y-auto w-full"
        ),
    )


def extra_langflow(add=False) -> rx.component:
    prefix = get_page_id_prefix(Page.control_panel if add else Page.main)
    return rx.accordion_item(
        rx.accordion_button(
            rx.text("Langflow"),
            rx.accordion_icon(),
            class_name=ACCORDION_BUTTON_CLS,
        ),
        rx.accordion_panel(
            wrap_row(
                rx.checkbox("Enable",
                            id=f"{prefix}add_langflow_enable" if add else f"{prefix}extra_langflow_enable",
                            class_name=add_class_tag(
                                TEXT_COLOR_CLASS, "text-sm d-flex align-items-center"),
                            ),
                add_cls="w-full"
            ),
            rx.cond(
                add,
                rx.cond(
                    EnvState.langflow_action_in_progress,
                    progress_log_panel("langflow"),
                    component_action_panel("langflow"),
                ),
            ),
            class_name="overflow-y-auto w-full"
        ),
    )
