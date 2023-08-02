import reflex as rx
from app.state.control_panel import ControlPanelState
from app.state.paperspace import PaperspaceState
from app.utils.components import *
from app.utils.constants import *
from reflex import el
from .paperspace_extra import *
from .paperspace import extra_options

import logging
logger = logging.getLogger(__name__)

prefix = get_page_id_prefix(page_id=Page.control_panel)

def prepare_general_tab() -> rx.Component:
    return el.div(
        wrap_row(
            *wrap_tooltip(
                specialButton(
                    rx.icon(tag="repeat"),
                    id="sync-control-panel-setting",
                    class_name=NORMAL_BUTTON_CLS,
                    size="md",
                    special_on_click=[
                        "updateRefValues(base_state, ref_mapping);"]
                ),
                title="Sync checkbox selection from setting",
            ),
            rx.cond(
                ControlPanelState.task_in_progress['upgrade_toolbox'],
                rx.circular_progress(is_indeterminate=True),
                rx.button(
                    "Upgrade Toolbox",
                    class_name=NORMAL_BUTTON_CLS,
                    size="md",
                    on_click=[
                        lambda: ControlPanelState.set_task_in_progress(
                            "upgrade_toolbox"),
                        ControlPanelState.upgrade_toolbox,
                    ]
                    # special_on_click=[
                    # "set_task_progress('upgrade_toolbox', true)",
                    # "execure_remote_command('cd /notebooks && git pull',null, 'Toolbox upgraded successfully.','Toolbox upgrade failed.')",
                    # "set_task_progress('upgrade_toolbox', false)",
                    # ]
                ),
            ),
            rx.cond(
                ControlPanelState.task_in_progress['get_storage_size'],
                rx.circular_progress(is_indeterminate=True),
                rx.button(
                    "Get Storage Usage",
                    class_name=NORMAL_BUTTON_CLS,
                    size="md",
                    on_click=[
                        lambda: ControlPanelState.set_task_in_progress(
                            "get_storage_size"),
                        ControlPanelState.get_storage_size,
                    ]
                    # special_on_click=[
                    # "set_task_progress('get_storage_size', true)",
                    # "execure_remote_command('du -sh /storage',null, 'Toolbox upgraded successfully.','Toolbox upgrade failed.')",
                    # ]
                ),
            ),
        ),
        extra_options(add=True),
        # wrap_row(
        #     rx.cond(
        #         ControlPanelState.task_in_progress['install_components'],
        #         rx.circular_progress(is_indeterminate=True),
        #         rx.button(
        #             "Install",
        #             class_name=NORMAL_BUTTON_CLS,
        #             size="md",
        #             on_click=[
        #                 lambda: ControlPanelState.set_task_in_progress("install_components"),
        #                 lambda: ControlPanelState.install_components(get_ref_value_fn(prefix="control_panel")),
        #             ]
        #         ),
        #     ),
        #     add_cls="pt-5",
        #     justify_content="end"
        # ),
    )


def prepare_huggingface_upload_select() -> rx.Component:
    return el.div(
        wrap_row(
            component_with_title(
                "Huggingface Token (Need write permission)",
                rx.input,
                input_kwargs={"id": f"{prefix}huggingface_token"},
                vstack_kwargs={'class_name': "min-w-fit",
                               "align_items": "start"}
            ),
            component_with_title(
                "Repo ID",
                rx.input,
                input_kwargs={"id": f"{prefix}huggingface_target_repo_id"},
                vstack_kwargs={'class_name': "min-w-fit pl-3",
                               "align_items": "start"}
            ),
            rx.checkbox("Private (Only apply if target repo does not exist)",
                        input_kwargs={
                            "id": f"{prefix}huggingface_repo_is_private"},
                        class_name=add_class_tag(
                            TEXT_COLOR_CLASS, "text-sm d-flex align-items-center pl-5"),
                        ),
        ),
        rx.cond(
            ControlPanelState.huggingface_mode == "Upload Folder",
            wrap_row(
                component_with_title(
                    "Path to target folder",
                    rx.input,
                    input_kwargs={
                        "id": f"{prefix}huggingface_target_folder_path"},
                    vstack_kwargs={'class_name': "w-full",
                                   "align_items": "start"}
                ),
            ),
        ),
        rx.cond(
            ControlPanelState.huggingface_mode == "Upload File",
            wrap_row(
                component_with_title("Comma separated list of files to upload",
                                     rx.text_area,
                                     input_kwargs={
                                         "id": f"{prefix}huggingface_target_files"},
                                     vstack_kwargs={"class_name": "w-full",
                                                    "align_items": "start"}
                                     ),
            ),
        ),
        wrap_row(
            rx.cond(
                ControlPanelState.task_in_progress['huggingface_upload'],
                rx.circular_progress(is_indeterminate=True),
                rx.button(
                    "Upload",
                    class_name=NORMAL_BUTTON_CLS,
                    size="md",
                    on_click=[
                        lambda: ControlPanelState.set_task_in_progress(
                            "huggingface_upload"),
                        lambda: ControlPanelState.upload_to_hf(
                            get_ref_value_fn(prefix="control_panel")),
                    ]
                ),
            ),
            rx.button(
                "Back",
                class_name=NORMAL_BUTTON_CLS,
                size="md",
                on_click=[
                    lambda: ControlPanelState.set_huggingface_step(
                        "select_mode"),
                ]
            ),
            add_cls="pt-4",
        )
    )


def prepare_huggingface_select_mode() -> rx.Component:
    return el.div(
        wrap_row(
            rx.radio_group(
                rx.hstack(
                    rx.radio("Upload Folder"),
                    rx.radio("Upload File"),
                    spacing="2em"
                ),
                on_change=ControlPanelState.set_huggingface_mode,
            ),
            add_cls="pt-4",
        ),
        wrap_row(
            rx.button(
                "Next",
                bg="blue.600",
                class_name="text-gray1",
                size="md",
                on_click=[
                    lambda: ControlPanelState.set_huggingface_step(
                        "select_target"),
                ]
            ),
            add_cls="pt-4",
        ),
    )


def prepare_model_download_tab() -> rx.Component:
    return rx.accordion(
        prepare_t2i_model_selection(add=True),
        extra_llm_model_download(add=True),
        default_index=[0,1],
        width="100%",
        allow_multiple=True,
        allow_toggle=False,
    )


def prepare_image_tab() -> rx.Component:
    return el.div(
        wrap_card(
            wrap_row(
                rx.heading(
                    "Compress folder and link to /notebooks", size="md"),
            ),
            component_with_title(
                "Target folder",
                rx.input,
                input_kwargs={"id": f"{prefix}zip_target_path"},
                vstack_kwargs={'class_name': "min-w-fit",
                               "align_items": "start"}
            ),
            wrap_row(
                rx.cond(
                    ControlPanelState.task_in_progress['compress_folder'],
                    rx.text(ControlPanelState.task_progress['compress'],
                            class_name="pl-4", size="sm"),
                    rx.button(
                        "Compress",
                        bg="blue.600",
                        class_name="text-gray1",
                        size="md",
                        on_click=[
                            lambda: ControlPanelState.set_task_in_progress(
                                "compress_folder"),
                            lambda: ControlPanelState.compress_folder(
                                get_ref_value_fn([f"{prefix}zip_target_path"])),
                        ]
                    ),
                ),
                add_cls="pt-4",
            ),
            # width="90%",

        ),
        wrap_card(
            wrap_row(
                rx.heading("Upload to Huggingface Hub", size="md"),
            ),
            rx.cond(
                ControlPanelState.huggingface_step == "select_mode",
                prepare_huggingface_select_mode()
            ),
            rx.cond(
                ControlPanelState.huggingface_step == "select_target",
                prepare_huggingface_upload_select()
            ),
            # width="90%",
        ),
    )


def prepare_monitor_tab() -> rx.Component:
    return el.div(
        wrap_card(
            wrap_row(
                rx.heading("GPU usage", size="md"),
            ),
            rx.cond(
                ControlPanelState.monitor_content["gpu_usage"] != "",
                custom_code_block(
                    ControlPanelState.monitor_content['gpu_usage'])
            ),
        ),
        wrap_card(
            wrap_row(
                rx.heading("Component Status", size="md"),
            ),
            rx.cond(
                ControlPanelState.monitor_content['component'] != "",
                custom_code_block(
                    ControlPanelState.monitor_content['component'])
            ),
        ),
        wrap_card(
            wrap_row(
                rx.heading("Running process", size="md"),
            ),
            rx.cond(
                ControlPanelState.monitor_content['process'] != "",
                custom_code_block(
                    ControlPanelState.monitor_content['process'])
            ),
        ),
        wrap_row(
            rx.cond(
                ControlPanelState.task_in_progress['monitor'],
                rx.button(
                    "Interrupt",
                    bg="red.600",
                    class_name="text-gray1 ",
                    size="md",
                    on_click=[
                        lambda: PaperspaceState.interrupt_task("monitor"),
                    ]
                ),
                rx.button(
                    "Monitor",
                    bg="blue.600",
                    class_name="text-gray1",
                    size="md",
                    on_click=[
                        lambda: ControlPanelState.set_task_in_progress(
                            'monitor'),
                        ControlPanelState.monitor,
                        # EnvState.set_env_id(EnvState.env_id),
                    ]
                ),
            ),
            add_cls="pt-4"
        ),
    )


def prepare_shell_tab() -> rx.Component:
    return el.div(
        wrap_card(
            component_with_title(
                "Command",
                rx.text_area,
                input_kwargs={"id": f"{prefix}shell_command"},
                vstack_kwargs={
                    'class_name': "min-w-fit pb-5", "align_items": "start"}
            ),
            rx.cond(
                ControlPanelState.shell_result != "",
                custom_code_block(ControlPanelState.shell_result)
            ),
            wrap_row(
                rx.cond(
                    ControlPanelState.task_in_progress['shell'],
                    rx.circular_progress(is_indeterminate=True),
                    rx.button(
                        "Send",
                        bg="blue.600",
                        class_name="text-gray1",
                        size="md",
                        on_click=[
                            lambda: ControlPanelState.set_task_in_progress(
                                "shell"),
                            lambda: ControlPanelState.shell_execute(
                                get_ref_value_fn(prefix="control_panel")),
                            # EnvState.set_env_id(EnvState.env_id),
                        ]
                    ),
                ),
            ),
        ),
    )


def get_control_panel() -> rx.Component:
    prefix = get_page_id_prefix(page_id=Page.control_panel)
    return el.div(
        wrap_card(
            wrap_row(
                # component_with_title(
                #     "Command Server URL",
                #     rx.input,
                #     input_kwargs={"id" : f"{prefix}extra_command_url"},
                #     # input_kwargs={"id": f"{prefix}extra_command_url",
                #     #               "on_blur": EnvState.set_extra_command_url},
                #     # vstack_kwargs={'class_name': "w-4/12", "align_items": "start"}
                # ),
                component_with_title("Command Server Username",
                                     rx.input,
                                     # input_kwargs={"id": f"{prefix}extra_command_user"},
                                     input_kwargs={
                                         "id": f"{prefix}extra_command_user", "on_blur": EnvState.set_extra_command_user},
                                     # vstack_kwargs={"class_name": "w-2/12", "align_items": "start"}/
                                     ),
                component_with_title("Command Server Password",
                                     rx.input,
                                     # input_kwargs={"id": f"{prefix}extra_command_password"},
                                     input_kwargs={
                                         "id": f"{prefix}extra_command_password", "on_blur": EnvState.set_extra_command_password},
                                     # vstack_kwargs={"class_name": "w-2/12", "align_items": "start"}
                                     ),
                add_cls="overflow-y-auto w-full",
            ),
            rx.tabs(
                rx.tab_list(
                    rx.tab("General"),
                    rx.tab("Model Download"),
                    rx.tab("File Transfer"),
                    rx.tab("Monitor"),
                    rx.tab("Shell"),
                    class_name="overflow-y-auto w-full",
                ),
                rx.tab_panels(
                    rx.tab_panel(prepare_general_tab()),
                    rx.tab_panel(prepare_model_download_tab()),
                    rx.tab_panel(prepare_image_tab()),
                    rx.tab_panel(prepare_monitor_tab()),
                    rx.tab_panel(prepare_shell_tab()),
                ),
                class_name="text-sm font-medium text-center text-gray-500 border-b border-gray-200 dark:text-gray-400 dark:border-gray-700 overflow-y-auto w-full"
            ),
            width="90%",
        ),
        class_name="md:pt-6 h-full w-full flex align-items-center justify-center",
    )
