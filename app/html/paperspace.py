from app.utils.components import *
from app.utils.constants import *
from app.utils.functions import *
from app.state.paperspace import PaperspaceState, NewEnvState, EnvState
from .paperspace_extra import *
import reflex as rx
from reflex import el
from reflex.vars import BaseVar

import logging
logger = logging.getLogger(__name__)


def prepare_upload_modal() -> rx.Component:
    output = el.div(
        el.button(
            "Import",
            class_name=TEXT_COLOR_CLASS,
            type="button",
            custom_attrs={'data-modal-target': 'upload-select-modal',
                          'data-modal-toggle': 'upload-select-modal'
                          }
        ),
        el.div(
            el.div(
                el.div(
                    el.div(
                        el.h3(
                            "Upload",
                            class_name="text-xl font-semibold text-gray-900 dark:text-white",
                        ),
                        el.button(
                            rx.html('''<svg aria-hidden='true' class='w-5 h-5' fill='currentColor' viewbox='0 0 20 20' xmlns='http://www.w3.org/2000/svg'><path clip-rule='evenodd' d='M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z' fill-rule='evenodd'></path></svg>'''),
                            el.span(
                                "Close modal",
                                class_name="sr-only",
                            ),
                            type="button",
                            class_name="text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm p-1.5 ml-auto inline-flex items-center dark:hover:bg-gray-600 dark:hover:text-white",
                            custom_attrs={
                                'data-modal-hide': 'upload-select-modal'}
                        ),
                        class_name="flex items-start justify-between p-4 border-b rounded-t dark:border-gray-600",
                    ),
                    wrap_row(
                        rx.upload(
                            rx.vstack(
                                el.button(
                                    "Select File",
                                    class_name=NORMAL_BUTTON_CLS,
                                    type="button",
                                    # color=color,
                                ),
                                rx.text(
                                    "Drag and drop files here or click to select files",
                                    class_name=TEXT_COLOR_CLASS,
                                ),
                            ),
                            border="1px dotted rgb(107,99,246)",
                            padding="5em",
                            multiple=False,
                            accept={
                                "application/json": ['.json'],
                            },
                        ),
                        add_cls="flex flex-col items-center justify-center pt-2"
                    ),
                    el.div(
                        el.button(
                            "Upload",
                            type="button",
                            class_name=NORMAL_BUTTON_CLS,
                            on_click=lambda: EnvState.import_env(
                                rx.upload_files()
                            ),
                            custom_attrs={
                                'data-modal-hide': 'upload-select-modal'}
                        ),
                        el.button(
                            "Cancel",
                            type="button",
                            class_name="text-gray-500 bg-white hover:bg-gray-100 focus:ring-4 focus:outline-none focus:ring-blue-300 rounded-lg border border-gray-200 text-sm font-medium px-5 py-2.5 hover:text-gray-900 focus:z-10 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-500 dark:hover:text-white dark:hover:bg-gray-600 dark:focus:ring-gray-600",
                            custom_attrs={
                                'data-modal-hide': 'upload-select-modal'}
                        ),
                        class_name="flex items-center p-6 space-x-2 border-t border-gray-200 rounded-b dark:border-gray-600",
                    ),
                    class_name="relative bg-white rounded-lg shadow dark:bg-gray-700",
                ),
                class_name="relative w-full max-w-2xl max-h-full",
            ),
            id="upload-select-modal",
            tab_index="-1",
            class_name="fixed top-0 left-0 right-0 z-50 hidden w-full p-4 overflow-x-hidden overflow-y-auto md:inset-0 h-[calc(100%-1rem)] max-h-full",
            custom_attrs={'aria-hidden': 'true'}
        )
    )
    return output


def prepare_existing_env_form() -> rx.Component:
    prefix = get_page_id_prefix(Page.main)
    output = wrap_card(
        wrap_row(
            component_with_title("Environment Name",
                                 rx.input,
                                 input_kwargs={
                                     'id': f"{prefix}env_name", 'is_required': True},
                                 vstack_kwargs={'align_items': "start"},
                                 ),
            # save_api_key_checkbox(),
        ),
        wrap_row(
            component_with_title("Project ID",
                                 rx.input,
                                 input_kwargs={
                                     "id": f"{prefix}env_project_id", 'is_required': True},
                                 vstack_kwargs={'align_items': "start"},
                                 ),
            component_with_title("Notebook ID",
                                 rx.input,
                                 input_kwargs={
                                     "id": f"{prefix}env_notebook_id", 'is_required': True},
                                 vstack_kwargs={'align_items': "start"},
                                 ),
            add_cls="w-full"
        ),
        add_cls="w-full"
    )
    return output


def workspace_advanced() -> rx.component:
    prefix = get_page_id_prefix(Page.main)
    output = el.div(
        wrap_row(
            component_with_title("Workspace Ref (Optional)",
                                 rx.input,
                                 input_kwargs={
                                     "id": f"{prefix}env_workspace_ref"},
                                 vstack_kwargs={"align_items": "start"}
                                 ),
            add_cls="w-full"
        ),
        wrap_row(
            component_with_title("Workspace Username (Optional)",
                                 rx.input,
                                 input_kwargs={
                                     "id": f"{prefix}env_workspace_username"},
                                 vstack_kwargs={"align_items": "start"}
                                 ),
            component_with_title("Workspace Password (Optional)",
                                 rx.input,
                                 input_kwargs={
                                     "id": f"{prefix}env_workspace_password"},
                                 vstack_kwargs={"align_items": "start"}
                                 ),
            add_cls="w-full"
        ),
    )
    return output


def container_advanced() -> rx.component:
    prefix = get_page_id_prefix(Page.main)
    output = el.div(
        wrap_row(
            component_with_title("Container Username (Optional)",
                                 rx.input,
                                 input_kwargs={
                                     "id": f"{prefix}env_registry_username"},
                                 vstack_kwargs={"align_items": "start"}
                                 ),
            component_with_title("Container Password (Optional)",
                                 rx.input,
                                 input_kwargs={
                                     "id": f"{prefix}env_registry_password"},
                                 vstack_kwargs={"align_items": "start"}
                                 ),
            add_cls="w-full"
        )
    )
    return output


def extra_options(add=False) -> rx.component:
    utilities = [] if add else [extra_command(add)]
    #extra_cloudflare(add),
    utilities += [
                  extra_minio(add),
                  extra_rclone(add),
                  extra_discord(add),
                ]
    sd = [
        extra_sd_webui(add),
        extra_sd_comfy(add),
        extra_sd_fooocus(add),
        extra_sd_simplesdxl(add),
        extra_preprocess(add),
        # extra_sd_volta(add),
        extra_t2i_image_browser(add)
    ]
    if not add:
        sd += [prepare_t2i_model_selection(add)]
    return rx.accordion(
        rx.accordion_item(
            rx.accordion_button(
                rx.text("Stable Diffusion"),
                rx.accordion_icon(),
                class_name=ACCORDION_BUTTON_CLS,
            ),
            rx.accordion_panel(*sd),
        ),
        rx.accordion_item(
            rx.accordion_button(
                rx.text("Large Language Model (LLM)"),
                rx.accordion_icon(),
                class_name=ACCORDION_BUTTON_CLS,
            ),
            rx.accordion_panel(
                extra_textgen(add),
                # extra_fastchat(add),
                extra_flowise(add),
                extra_langflow(add),
                extra_llm_model_download(add),
            ),
        ),
        rx.accordion_item(
            rx.accordion_button(
                rx.text("Other"),
                rx.accordion_icon(),
                class_name=ACCORDION_BUTTON_CLS,
            ),
            rx.accordion_panel(
                extra_musicgen(add),
                extra_kosmos2(add),
            ),
        ),
        rx.accordion_item(
            rx.accordion_button(
                rx.text("Utilities"),
                rx.accordion_icon(),
                class_name=ACCORDION_BUTTON_CLS,
            ),
            rx.accordion_panel(
                *utilities,
            ),
        ),
        width="100%",
        allow_multiple=True,
        allow_toggle=False,
    )


def env_for_new_notebook() -> rx.Component:
    prefix = get_page_id_prefix(Page.main)
    output = wrap_card(
        wrap_row(
            component_with_title("Environment Name",
                                 rx.input,
                                 input_kwargs={
                                     'id': f"{prefix}env_name", 'is_required': True},
                                 vstack_kwargs={'align_items': "start"},
                                 ),
            # TODO: not sure how to change select to use id and ref
            component_with_title("Auto-shutdown timeout",
                                 rx.select,
                                 rx.foreach(
                                     paperspace_timeout_options,
                                     lambda o: rx.option(
                                         o, class_name=SELECT_OPTION_CLS),
                                 ),
                                 input_kwargs={"id": f"{prefix}env_auto_timeout",
                                               # 'default_value': EnvState.env_auto_timeout,
                                               #    'on_change': EnvState.set_env_auto_timeout,
                                               'is_required': True,
                                               },
                                 vstack_kwargs={'align_items': "start"},
                                 ),
            # save_api_key_checkbox(),
            add_cls="w-full"
        ),
        wrap_row(
            component_with_title("Workspace",
                                 rx.input,
                                 input_kwargs={"id": f"{prefix}env_workspace"},
                                 vstack_kwargs={
                                     'class_name': "w-full", "align_items": "start"}
                                 ),
            add_cls="w-full"
        ),
        workspace_advanced(),
        wrap_row(
            component_with_title("Container",
                                 rx.input,
                                 input_kwargs={"id": f"{prefix}env_container"},
                                 vstack_kwargs={
                                     'class_name': "w-full", "align_items": "start"}
                                 ),
            add_cls="w-full"
        ),
        container_advanced(),
        wrap_row(
            component_with_title("Command",
                                 rx.input,
                                 input_kwargs={"id": f"{prefix}env_command"},
                                 vstack_kwargs={
                                     'class_name': "w-full", "align_items": "start"}
                                 ),
            add_cls="w-full"
        ),
        extra_options(),
        add_cls="w-full"
    )
    return output


def prepare_sync_env_button() -> rx.Component:
    output = el.div(
        # button = el.button(
        #     component,
        #     el.span(
        #         title,
        #         class_name="sr-only",
        #     ),
        #     type="button",
        #     **button_kwargs
        # )
        *wrap_tooltip(
            el.button(
                rx.icon(tag="repeat"),
                size='sm',
                id="sync-env-button",
                class_name=BUTTON_CLS,
                on_click=[
                    EnvState.sync(get_ref_value_fn(refs=["main__env_api_key"]))
                ]
            ),
            title="Sync environment from Paperspace",
            tooltip_id="tooltip-sync-env-button",
        )
    )
    return output


def prepare_create_env_select_button() -> rx.Component:
    create_button = el.button(
        rx.icon(tag="add"),
        size='sm',
        id="create-env-select-button",
        class_name="inline-flex items-center p-2 text-sm font-medium text-center text-gray-900 bg-white rounded-lg hover:bg-gray-100 focus:ring-4 focus:outline-none dark:text-white focus:ring-gray-50 dark:bg-gray-800 dark:hover:bg-gray-700 dark:focus:ring-gray-600",
        custom_attrs={'data-dropdown-toggle': 'env-select-dropdown'},
    )
    menu = el.div(
        el.ul(
            el.li(
                el.a(
                    "Existing notebook",
                    href="#",
                    class_name="block px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white dropdown-item",
                    on_click=[
                        EnvState.clear,
                        lambda: PaperspaceState.set_env_type("existing"),
                    ]
                )
            ),
            el.li(
                el.a(
                    "New notebook",
                    href="#",
                    class_name="block px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white dropdown-item",
                    on_click=[
                        EnvState.clear,
                        lambda: PaperspaceState.set_env_type("new"),
                    ]
                )
            ),
            class_name="py-2 text-sm text-gray-700 dark:text-gray-200",
            custom_attrs={'aria-labelledby': 'create-env-select-button'},
        ),
        id="env-select-dropdown",
        class_name="z-10 hidden bg-white divide-y divide-gray-100 rounded-lg shadow w-44 dark:bg-gray-700 dark:divide-gray-600",
    )
    return el.div(
        create_button,
        menu
    )

def prepare_copy_button() -> rx.Component:
    return el.div(
            *wrap_tooltip(
                rx.button(
                rx.icon(tag="copy"),
                size='sm',
                id="copy-env-button",
                class_name="inline-flex items-center p-2 text-sm font-medium text-center text-gray-900 bg-white rounded-lg hover:bg-gray-100 focus:ring-4 focus:outline-none dark:text-white focus:ring-gray-50 dark:bg-gray-800 dark:hover:bg-gray-700 dark:focus:ring-gray-600",
                is_disabled=rx.cond(
                    PaperspaceState.is_env_selected, False, True),
                on_click=[
                    lambda: EnvState.copy_env(
                        get_ref_value_fn(prefix="main")),
                    PaperspaceState.update_envs,
                ]
            ),
                "Copy a new environment",
        )
    )

def prepare_gpu_list(gpu_list) -> rx.Component:
    prefix = get_page_id_prefix(Page.main)
    return el.div(
        *[
            rx.checkbox(gpu,
                        id=f"{prefix}gpu_list__{ALL_GPU.index(gpu)}",
                        class_name=EnvState.gpu_available[gpu],
                        width="100%",
                        )
            for gpu in gpu_list
        ],
    )


def prepare_gpu_panel() -> rx.Component:
    gpu_panel = wrap_card(
        rx.vstack(
            el.h5(
                "Gpu Manager",
                class_name=HEADING_CLASS,
                align="center"
            ),
            wrap_row(
                rx.accordion(
                    *[
                        rx.accordion_item(
                            rx.accordion_button(
                                rx.text(title),
                                rx.accordion_icon(),
                                class_name=ACCORDION_BUTTON_CLS,
                            ),
                            rx.accordion_panel(
                                prepare_gpu_list(gpu_list),
                            ),
                        )
                        for title, gpu_list in GPU_TIER
                    ],
                    # class_name="mr-2",
                    width="100%",
                    allow_multiple=True,
                    allow_toggle=False,
                ),
                justify="center"
            ),
            # width="100%",
        )
    )
    return gpu_panel


def prepare_env_panel() -> rx.Component:
    env_panel = wrap_card(
        rx.vstack(
            el.h5(
                "Environment Manager",
                class_name=HEADING_CLASS,
                align="center"
            ),
            rx.vstack(
                wrap_row(
                    el.div(
                        rx.select(
                            # BaseVar(name=f'{env.name}.name') cannot use "name" in Model, or it will conflict with name in BaseVar, which is a random var name for js
                            rx.foreach(PaperspaceState.environments,
                                       lambda env: rx.option(
                                           env.env_name,
                                           value=env.id,
                                           class_name=SELECT_OPTION_CLS,
                                       )),
                            id="env-select",
                            placeholder="Env",
                            on_change=[
                                lambda: EnvState.set_env_type(""),
                                EnvState.load_env,
                            ],
                            value=EnvState.env_id,
                            # width="50%"
                            class_name=TEXT_COLOR_CLASS,
                        ),
                        style={"minWidth": "100px"},

                    ),
                    prepare_create_env_select_button(),
                    prepare_copy_button(),
                    prepare_sync_env_button(),
                ),
                rx.cond(
                    PaperspaceState.env_type == "existing",
                    prepare_existing_env_form(),
                ),
                rx.cond(
                    PaperspaceState.env_type == "new",
                    env_for_new_notebook(),
                ),
                width="100%",
                class_name="min-w-fit"
                # justify_content="center"
            ),
            wrap_row(
                prepare_upload_modal(),
                rx.link(
                    el.button("Export", class_name=TEXT_COLOR_CLASS),
                    class_name="pl-2 pr-4",
                    size="md",
                    href=EnvState.get_env_download_link,
                    button=True,
                    is_external=True,
                ),
                rx.button(
                    "Save",
                    bg="blue.600",
                    class_name=BUTTON_TEXT_CLS,
                    size="md",
                    is_disabled=rx.cond(
                        PaperspaceState.is_env_selected, False, True),
                    on_click=[
                        lambda: EnvState.save_env(
                            get_ref_value_fn(prefix="main")),
                        PaperspaceState.update_envs,
                    ]
                ),
                rx.button(
                    "Delete",
                    bg="red.600",
                    class_name=BUTTON_TEXT_CLS,
                    size="md",
                    is_disabled=rx.cond(
                        PaperspaceState.is_env_selected, False, True),
                    on_click=lambda: EnvState.del_env(EnvState.env_id)
                ),
                justify="end"
            ),
            style={"paddingTop": "20px"},
            spacing="30px",
            justify="center"
        ),
        add_cls="w-full",
    )
    return env_panel


def prepare_power_panel() -> rx.Component:
    prefix = get_page_id_prefix(Page.main)
    power_panel = wrap_card(
        wrap_row(
            el.div(
                # power light
                rx.html('''<svg aria-hidden='true' class='w-6 h-6' fill='currentColor' viewBox='0 0 20 20' xmlns='http://www.w3.org/2000/svg'>
                            <path clip-rule='evenodd' d='M10 2a.75.75 0 01.75.75v7.5a.75.75 0 01-1.5 0v-7.5A.75.75 0 0110 2zM5.404 4.343a.75.75 0 010 1.06 6.5 6.5 0 109.192 0 .75.75 0 111.06-1.06 8 8 0 11-11.313 0 .75.75 0 011.06 0z' fill-rule='evenodd'></path>
                        </svg>'''
                        ),
                class_name=BaseVar(
                    name=f"text-${PaperspaceState.power_light}", is_local=True, is_string=True)
            ),
            rx.cond(
                PaperspaceState.display_retry_count,
                rx.text(
                    PaperspaceState.retry_count_str,
                    class_name=add_class_tag(TEXT_COLOR_CLASS, "text-sm"),
                ),
            ),
        ),
        rx.vstack(
            el.h5(
                "Power Control",
                class_name=HEADING_CLASS,
                align="center"
            ),
            component_with_title("Paperspace API Key",
                                 rx.input,
                                 input_kwargs={'id': f"{prefix}env_api_key"},
                                 vstack_kwargs={'class_name': "w-full pb-2",
                                                "align_items": "start"}
                                 ),
            rx.cond(
                PaperspaceState.show_progress_for_start_button,
                rx.button(
                    "Interrupt",
                    bg="red.600",
                    class_name=BUTTON_TEXT_CLS,
                    size="md",
                    on_click=[
                        lambda: PaperspaceState.interrupt_task(
                            "start_notebook"),
                    ]
                ),
                rx.button(
                    PaperspaceState.power_button,
                    class_name=NORMAL_BUTTON_CLS,
                    size="md",
                    on_click=[
                        lambda: PaperspaceState.set_show_progress_for_start_button(
                            True),
                        lambda: EnvState.start_stop_notebook(
                            get_ref_value_fn(prefix="main")),
                    ]
                ),
            ),
            # style={"paddingTop": "20px"},
            # spacing="30px",
            justify="center"
        )
    )
    return power_panel


def get_paperpace_panel() -> rx.Component:
    output = el.div(
        rx.wrap(
            rx.vstack(
                rx.cond(
                    EnvState.notebook_url != "",
                    component_with_title(
                        "Notebook URL",
                        rx.link,
                        EnvState.notebook_url,
                        input_kwargs={
                            "href": EnvState.notebook_url, "is_external": True},
                        vstack_kwargs={"class_name": add_class_tag(
                            TEXT_COLOR_CLASS, "text-sm break-all w-[300px]")},
                    ),
                ),
                prepare_power_panel(),
                el.div(
                    prepare_gpu_panel(),
                    class_name="w-[300px]"
                ),
            ),
            # rx.spacer(),
            el.div(
                prepare_env_panel(),
                class_name="md:w-1/2 overflow-y-auto w-full"
            ),
            class_name="w-full",
            # template_areas="repeat(10, )"
            justify="center",
            align="center",
            spacing="2em",
            # min_child_width="300px",
            # padding="6em",
        ),
        class_name="h-full w-full flex align-items-center justify-center",
        # width="90%",
    )
    return output
