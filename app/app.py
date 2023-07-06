"""Welcome to reflex! This file outlines the steps to create a basic app."""
import reflex as rx
from reflex import el
from app.utils.constants import *

from redis import Redis

import os
import logging
log_level = os.getenv("APP_LOG_LEVEL", "INFO")
logging.basicConfig(level=log_level,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class BaseState(rx.State):
    show_alert: bool = False
    alert_header: str = ""
    alert_msg: str = ""
    
# import after BaseState to avoid circular import
from app.utils.components import *
from .state import PaperspaceState, EnvState, ControlPanelState
from .html import create_navbar, get_paperpace_panel, get_control_panel, prepare_footer

def prepare_alert() -> rx.Component:
    """
    Prepares an alert dialog component with header, body, and footer.

    Returns:
        A `rx.Component` instance representing the alert dialog.
    """
    return rx.alert_dialog(
        rx.alert_dialog_overlay(
            rx.alert_dialog_content(
                rx.alert_dialog_header(PaperspaceState.alert_header,
                                        class_name=HEADING_CLASS),
                rx.alert_dialog_body(
                    PaperspaceState.alert_msg,
                    class_name = add_class_tag(TEXT_COLOR_CLASS, "whitespace-pre-line")
                ),
                rx.alert_dialog_footer(
                    rx.button(
                        "Close",
                        on_click=PaperspaceState.set_show_alert(False),
                        class_name = NORMAL_BUTTON_CLS
                    )
                ),
                class_name = "bg-gray-200 dark:bg-gray-900"
            ),
        ),
        is_open=PaperspaceState.show_alert,
        close_on_overlay_click=True,
    )

def index() -> rx.Component:
    return el.div(
        # RemoteExecuteHook.create(task_progress=ControlPanelState.task_in_progress, base_state = BaseState),
        StateUpdater.create(vars_to_update = {key: value for key, value in EnvState.vars.items() if key.startswith(prefix_to_watch)},
                            hook_vars=[EnvState.env_id], # Only update when env_id changes to avoid unnecessary updates
                        ),
        el.div(
            create_navbar(),
            prepare_alert(),
            width="100%",
            # height="100vh",
        ),
        el.div(
            prepare_tab_content(get_paperpace_panel(), "main-content"),
            prepare_tab_content(get_control_panel(), "control-panel-content"),
            class_name="md:pt-6 pb-12",
            id = "main-display",
            width="100%",
            position='relative'
        ),
        el.div(
            prepare_footer(),
             width="100%",
        ),
        el.iframe(
            name="upload-frame",
            class_name = "hidden"
        ),
        class_name="bg-gray-200 dark:bg-gray-900 overflow-y-auto",
        height="100vh",
    )

style = {
    "font_family": "Comic Sans MS",
    "font_size": "16px",
}

dark_mode = el.script(src="/dark_mode.js", defer=True)
stylesheets = [
             "https://cdnjs.cloudflare.com/ajax/libs/flowbite/1.6.6/flowbite.min.css", 
             ]

# Add state and page to the app.
script_tag = el.script(
    src="https://cdnjs.cloudflare.com/ajax/libs/flowbite/1.6.6/flowbite.min.js"
    )

app = rx.App(state=BaseState, style=style, stylesheets=stylesheets)

from app.backend.helpers import download_json
app.api.add_api_route("/download_env/{token}", download_json)
app.add_page(index, 
             title="Paperspace AI Toolbox",
             description="A super toolbox for everyone to enjoy AI on Papaerspace",
             script_tags=[script_tag, dark_mode],
             on_load=PaperspaceState.update_envs if WEB_HOSTING == False else None)
app.compile()
