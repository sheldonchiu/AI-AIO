import pynecone as pc
from app.state.control_panel import ControlPanelState
from app.state.paperspace import PaperspaceState
from app.utils.components import *
from app.utils.constants import *
from pynecone import el
from .paperspace_extra import *
from .paperspace import extra_options

import logging
logger = logging.getLogger(__name__)

prefix = get_page_id_prefix(page_id=Page.control_panel)

def prepare_general_tab() -> pc.Component:
    return el.div(
        wrap_row(
            *wrap_tooltip(
                specialButton(
                    pc.icon(tag="repeat"),
                    id="sync-control-panel-setting",
                    class_name=NORMAL_BUTTON_CLS,
                    size="md",
                    special_on_click=["updateRefValues(base_state, ref_mapping);"]
                ),
                title="Sync checkbox selection from setting",
            ),              
            pc.cond(
                ControlPanelState.task_in_progress['upgrade_toolbox'],
                pc.circular_progress(is_indeterminate=True),
                pc.button(
                    "Upgrade Toolbox",
                    class_name=NORMAL_BUTTON_CLS,
                    size="md",
                    on_click=[
                        lambda: ControlPanelState.set_task_in_progress("upgrade_toolbox"),
                        ControlPanelState.upgrade_toolbox,
                    ]
                    # special_on_click=[
                        # "set_task_progress('upgrade_toolbox', true)",
                        # "execure_remote_command('cd /notebooks && git pull',null, 'Toolbox upgraded successfully.','Toolbox upgrade failed.')",
                        # "set_task_progress('upgrade_toolbox', false)",
                    # ]
                ),             
            ), 
            pc.cond(
                ControlPanelState.task_in_progress['get_storage_size'],
                pc.circular_progress(is_indeterminate=True),
                pc.button(
                    "Get Storage Usage",
                    class_name=NORMAL_BUTTON_CLS,
                    size="md",
                    on_click=[
                        lambda: ControlPanelState.set_task_in_progress("get_storage_size"),
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
        #     pc.cond(
        #         ControlPanelState.task_in_progress['install_components'],
        #         pc.circular_progress(is_indeterminate=True),
        #         pc.button(
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
       
def prepare_huggingface_upload_select() -> pc.Component:
    return el.div(
        wrap_row(
            component_with_title(
                "Huggingface Token (Need write permission)",
                pc.input,
                input_kwargs={"id" : f"{prefix}huggingface_token"},
                vstack_kwargs={'class_name': "min-w-fit", "align_items": "start"}
            ),            
            component_with_title(
                "Repo ID",
                pc.input,
                input_kwargs={"id" : f"{prefix}huggingface_target_repo_id"},
                vstack_kwargs={'class_name': "min-w-fit pl-3", "align_items": "start"}
            ),
            pc.checkbox("Private (Only apply if target repo does not exist)", 
                input_kwargs={"id" : f"{prefix}huggingface_repo_is_private"},
                class_name=add_class_tag(TEXT_COLOR_CLASS, "text-sm d-flex align-items-center pl-5"),
            ), 
        ),
        pc.cond(
            ControlPanelState.huggingface_mode == "Upload Folder",
            wrap_row(
                component_with_title(
                    "Path to target folder",
                    pc.input,
                    input_kwargs={"id" : f"{prefix}huggingface_target_folder_path"},
                    vstack_kwargs={'class_name': "w-full", "align_items": "start"}
                ),        
            ),
        ),
        pc.cond(
            ControlPanelState.huggingface_mode == "Upload File",
            wrap_row(
                component_with_title("Comma separated list of files to upload",
                    pc.text_area,
                    input_kwargs={"id" : f"{prefix}huggingface_target_files"},
                    vstack_kwargs={"class_name": "w-full", "align_items": "start"}
                ),  
            ),
        ),
        wrap_row(
            pc.cond(
                ControlPanelState.task_in_progress['huggingface_upload'],
                pc.circular_progress(is_indeterminate=True),
                pc.button(
                    "Upload",
                    class_name=NORMAL_BUTTON_CLS,
                    size="md",
                    on_click=[
                        lambda: ControlPanelState.set_task_in_progress("huggingface_upload"),
                        lambda: ControlPanelState.upload_to_hf(get_ref_value_fn(prefix="control_panel")),
                    ]
                ),                
            ),
            pc.button(
                "Back",
                class_name=NORMAL_BUTTON_CLS,
                size="md",
                on_click=[
                    lambda: ControlPanelState.set_huggingface_step("select_mode"),
                ]
            ),  
            add_cls="pt-4",  
        )
    )
    
def prepare_huggingface_select_mode() -> pc.Component:
    return el.div(
            wrap_row(
            pc.radio_group(
                pc.hstack(
                    pc.radio("Upload Folder"), 
                    pc.radio("Upload File"),   
                    spacing="2em"            
                ),
                on_change=ControlPanelState.set_huggingface_mode,
            ),
            add_cls="pt-4",
        ),
            wrap_row(
                pc.button(
                    "Next",
                    bg="blue.600",
                    class_name="text-gray1",
                    size="md",
                    on_click=[
                        lambda: ControlPanelState.set_huggingface_step("select_target"),
                    ]
                ),   
                add_cls="pt-4",             
            ),
    )

def prepare_image_tab() -> pc.Component:
    return el.div(
        wrap_card(
            wrap_row(
                pc.heading("Compress folder and link to /notebooks", size="md"),
            ),
            component_with_title(
                "Target folder",
                pc.input,
                input_kwargs={"id" : f"{prefix}zip_target_path"},
                vstack_kwargs={'class_name': "min-w-fit", "align_items": "start"}
            ), 
            wrap_row(
                pc.cond(
                    ControlPanelState.task_in_progress['compress_folder'],
                    pc.text(ControlPanelState.compress_progress, class_name="pl-4",size="sm"),
                    pc.button(
                        "Compress",
                        bg="blue.600",
                        class_name="text-gray1",
                        size="md",
                        on_click=[
                            lambda: ControlPanelState.set_task_in_progress("compress_folder"),
                            lambda: ControlPanelState.compress_folder(get_ref_value_fn([f"{prefix}zip_target_path"])),
                        ]
                    ),                      
                ),
                add_cls="pt-4",             
            ),
            # width="90%",
            
        ),
        wrap_card(
            wrap_row(
                pc.heading("Upload to Huggingface Hub", size="md"),
            ),  
            pc.cond(
                ControlPanelState.huggingface_step == "select_mode",
                prepare_huggingface_select_mode()
            ),
            pc.cond(
                ControlPanelState.huggingface_step == "select_target",
                prepare_huggingface_upload_select()
            ),
            # width="90%",
        ),
    )
    
def prepare_monitor_tab() -> pc.Component:
    return el.div(
            wrap_card(
                wrap_row(
                    pc.heading("GPU usage", size="md"),
                ),
                pc.cond(
                    ControlPanelState.monitor_content["gpu_usage"] != "",
                    custom_code_block(ControlPanelState.monitor_content['gpu_usage'])
                ),
            ),   
            wrap_card(
                wrap_row(
                    pc.heading("Component Status", size="md"),
                ),
                pc.cond(
                    ControlPanelState.monitor_content['component'] != "",
                    custom_code_block(ControlPanelState.monitor_content['component'])
                ),
            ), 
            wrap_card(
                wrap_row(
                    pc.heading("Running process", size="md"),
                ),
                pc.cond(
                    ControlPanelState.monitor_content['process'] != "",
                    custom_code_block(ControlPanelState.monitor_content['process'])
                ),
            ), 
            wrap_row(
                pc.cond(
                    ControlPanelState.task_in_progress['monitor'],
                    pc.button(
                        "Interrupt",
                        bg="red.600",
                        class_name="text-gray1 ",
                        size="md",
                        on_click=[
                            lambda: PaperspaceState.interrupt_task("monitor"),
                        ]
                    ),
                    pc.button(
                        "Monitor",
                        bg="blue.600",
                        class_name="text-gray1",
                        size="md",
                        on_click=[
                            lambda: ControlPanelState.set_task_in_progress('monitor'),
                            ControlPanelState.monitor,
                            # EnvState.set_env_id(EnvState.env_id),
                        ]
                    ),    
                ),
                add_cls="pt-4"
            ),
    )   
    
def prepare_shell_tab() -> pc.Component:
    return el.div(
           wrap_card(
                component_with_title(
                    "Command",
                    pc.text_area,
                    input_kwargs={"id" : f"{prefix}shell_command"},
                    vstack_kwargs={'class_name': "min-w-fit pb-5", "align_items": "start"}
                ),  
                pc.cond(
                    ControlPanelState.shell_result != "",
                    custom_code_block(ControlPanelState.shell_result)
                ),
                wrap_row(
                    pc.cond(
                        ControlPanelState.task_in_progress['shell'],
                        pc.circular_progress(is_indeterminate=True),
                        pc.button(
                            "Send",
                            bg="blue.600",
                            class_name="text-gray1",
                            size="md",
                            on_click=[
                                lambda: ControlPanelState.set_task_in_progress("shell"),
                                lambda: ControlPanelState.shell_execute(get_ref_value_fn(prefix="control_panel")),
                                # EnvState.set_env_id(EnvState.env_id),
                            ]
                        ), 
                    ), 
                ),
           ),
    )

def get_control_panel() -> pc.Component:
    prefix = get_page_id_prefix(page_id=Page.control_panel)
    return el.div(
        wrap_card(
            wrap_row(
                component_with_title(
                    "Command Server URL",
                    pc.input,
                    input_kwargs={"id" : f"{prefix}extra_command_url"},
                    # vstack_kwargs={'class_name': "w-4/12", "align_items": "start"}
                ), 
                component_with_title("Command Server Username",
                    pc.input,
                    input_kwargs={"id": f"{prefix}extra_command_user"},
                    # vstack_kwargs={"class_name": "w-2/12", "align_items": "start"}/
                ),
                component_with_title("Command Server Password",
                    pc.input,
                    input_kwargs={"id": f"{prefix}extra_command_password"},
                    # vstack_kwargs={"class_name": "w-2/12", "align_items": "start"}
                ),
                add_cls="overflow-y-auto w-full",
            ),
            pc.tabs(
                pc.tab_list(
                    pc.tab("General"),
                    pc.tab("File Transfer"),
                    pc.tab("Monitor"),
                    pc.tab("Shell"),
                    class_name = "overflow-y-auto w-full",
                ),
                pc.tab_panels(
                    pc.tab_panel(prepare_general_tab()),
                    pc.tab_panel(prepare_image_tab()),
                    pc.tab_panel(prepare_monitor_tab()),
                    pc.tab_panel(prepare_shell_tab()),
                ),
                # items=[
                #     ("General", prepare_general_tab()),
                #     ("File Transfer", prepare_image_tab()),
                #     ("Monitor", prepare_monitor_tab()),
                #     ("Shell", prepare_shell_tab()),
                # ],
                class_name="text-sm font-medium text-center text-gray-500 border-b border-gray-200 dark:text-gray-400 dark:border-gray-700 overflow-y-auto w-full"
            ),
            width="90%",
        ),
        class_name="md:pt-6 h-full w-full flex align-items-center justify-center",
    )
