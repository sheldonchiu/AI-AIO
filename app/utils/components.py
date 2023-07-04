from app.utils.constants import *
import re
import reflex as rx
from reflex import el
from typing import Dict, Tuple, List, Optional, ClassVar, Type, Union, Any
from reflex.utils import types
from textwrap import dedent
from reflex.vars import Var
from jinja2 import Template
import json

import logging

logger = logging.getLogger(__name__)


def add_class_tag(*args: str) -> str:
    """
    Combines multiple class names into a single string, separated by spaces.

    Args:
        *args: Any number of strings representing class names.

    Returns:
        A string containing all the class names, separated by spaces.
    """
    class_name = ' '.join(args)
    return class_name


def wrap_card(*content: rx.Component, add_cls: str = None, **kwargs) -> rx.Component:
    """
    Wraps content in a card-like component with a white background, gray border, and shadow.

    Args:
        *content: Any number of components to wrap in the card.
        add_cls: Optional additional class name(s) to apply to the card.
        **kwargs: Any additional attributes to apply to the card.

    Returns:
        A `rx.Component` instance representing the wrapped card.
    """
    class_name = "p-6 bg-white border border-gray-200 rounded-lg shadow dark:bg-gray-800 dark:border-gray-700"
    if add_cls:
        class_name = add_class_tag(class_name, add_cls)
    return el.div(
        *content,
        class_name=class_name,
        **kwargs
    )


def wrap_row(*content: rx.Component, add_cls: str = None, **kwargs) -> rx.Component:
    """
    Wraps content in a row-like component with a flexible width.

    Args:
        *content: Any number of components to wrap in the row.
        add_cls: Optional additional class name(s) to apply to the row.
        **kwargs: Any additional attributes to apply to the row.

    Returns:
        A `rx.Component` instance representing the wrapped row.
    """
    class_name = "min-w-fit pb-3"
    if add_cls:
        class_name = add_class_tag(class_name, add_cls)
    return rx.wrap(
        *content,
        width="100%",
        class_name=class_name,
        # justify="start",
        # align_items="start",
        **kwargs
    )


def wrap_tooltip(content: rx.Component,
                 title: str,
                 tooltip_id: str = None,
                 ) -> Tuple[rx.Component, rx.Component]:
    """
    Creates a button component with a tooltip.

    Args:
        component: The component to use as the button content.
        title: The text to display in the tooltip.
        tooltip_id: Optional ID to use for the tooltip. Defaults to a generated ID.
        **button_kwargs: Additional attributes to apply to the button.

    Returns:
        A tuple of two `rx.Component` instances: the button and the tooltip.
    """
    tooltip_id = tooltip_id if tooltip_id else f"tooltip-{title.replace(' ', '-').lower()}"
    tooltip = el.div(
        title,
        el.div(
            class_name="tooltip-arrow",
            custom_attrs={'data-popper-arrow': ''},
        ),
        id=tooltip_id,
        role="tooltip",
        class_name=NORMAL_TOOLTIP_CLS,
    )
    content.custom_attrs['data-tooltip-target'] = tooltip_id
    return content, tooltip


def component_with_title(title: str,
                         component: rx.Component,
                         *component_args: rx.Component,
                         input_kwargs: Dict = {},
                         vstack_kwargs: Dict = {},
                         add_cls: str = "") -> rx.Component:
    """
    Wraps a component in a vertical stack with a title.

    Args:
        title: The text to display as the title.
        component: The component to wrap in the stack.
        *component_args: Any additional components to include in the stack.
        input_kwargs: Optional additional attributes to apply to the wrapped component.
        vstack_kwargs: Optional additional attributes to apply to the vertical stack.
        add_cls: Optional additional class name(s) to apply to the wrapped component.

    Returns:
        A `rx.Component` instance representing the wrapped component with a title.
    """
    return rx.vstack(
        rx.text(title, class_name=add_class_tag(
            TEXT_COLOR_CLASS, "text-sm")),
        # debounce_input(
        component(
            *component_args,
            class_name=add_class_tag(TEXT_COLOR_CLASS, add_cls),
            **input_kwargs,
        ),
        # debounce_timeout=-1,
        # force_notify_on_blur=True,
        # ),
        **vstack_kwargs,
    )


def custom_code_block(content: rx.Component, id: str = None) -> rx.Component:
    """
    Creates a custom code block component.

    Args:
        content: The content to display in the code block.

    Returns:
        A `rx.Component` instance representing the custom code block.
    """

    return rx.code_block(
        content,
        id=id,
        class_name="overflow-auto max-h-96 pt-2",
        language="bash",
        show_line_numbers=False,
        theme="dark",
        wrap_long_lines=True,
    )


class StateUpdater(rx.Component):
    """A component that defines a hook for updating state variables in a React component.

    Attributes:
        library (str): The path to the library containing the state utility functions.
        tag (str): The tag name for the component.
        hook_vars (List[Optional[Var]]): A list of variables to use in the hook.
        vars_to_update (List[Var]): A list of variables to update when the hook is called.
    """

    library = "/public/watcher"
    tag = "getRefValues,updateRefValues"

    var_name = "value"
    prefix = ""

    hook_vars: List[Union[Var, str]] = []
    update_control: str = None
    vars_to_update = {}

    def render(self) -> str:
        """This component has no visual element, it only defines a hook"""
        return ""

    def _get_hooks(self) -> Optional[str]:
        """Generate a hook for updating the specified variables.

        Returns:
            Optional[str]: A string containing the generated hook.
        """

        template_str = """
        const ref_mapping = {{ ref_mapping }};
        useEffect(() => {
            updateRefValues(base_state, ref_mapping);
        }{{ hook }})
            """

        if len(self.hook_vars) == 0:
            hook = ""
        else:
            hook = ',[' + ','.join([var.full_name
                                    if types._issubclass(type(var), Var) else var
                                   for var in self.hook_vars]) + ']'
        ref_mapping = {key: value.full_name for key,
                       value in self.vars_to_update.items()}

        return Template(dedent(template_str)).render(hook=hook,
                                                     ref_mapping=ref_mapping,
                                                     )


class RemoteExecuteHook(rx.Component):
    """A component that defines a hook for updating state variables in a React component.

    Attributes:
        library (str): The path to the library containing the state utility functions.
        tag (str): The tag name for the component.
        hook_vars (List[Optional[Var]]): A list of variables to use in the hook.
        vars_to_update (List[Var]): A list of variables to update when the hook is called.
    """

    library = "/public/api"
    tag = "executeCommand"
    is_default = True

    task_progress: Optional[Var]
    base_state: Optional[Type[rx.State]]

    def __init__(self, task_progress: Var, base_state: Type[rx.State], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_progress = task_progress
        self.base_state = base_state

    def render(self) -> str:
        """This component has no visual element, it only defines a hook"""
        return ""

    def _get_hooks(self) -> Optional[str]:
        template = '''
    const set_task_progress = (variable, condition) =>{
      {{ task_progress }}[variable] = condition;
      setBase_state({...base_state});
    };
    const control_panel_log_control = (control, display, status, content="") => {
        control = status;
        display = content;
        setBase_state({...base_state});
    };
    const execure_remote_command = async (command, env=null, success_msg=null, fail_msg=null, skip_msg=false) => {
        try {
            let append_env = "";
            const url = ref_main__extra_command_url.current.value;
            const username = ref_main__extra_command_user.current.value;
            const password = ref_main__extra_command_password.current.value;
            
            if (env != null){
                for (const [key, value] of Object.entries(env)) {
                    append_env += `${key}=${value} `;
                }
                command = append_env + command;
            }

            const result = await executeCommand(url, command, username, password);
            if (result.code != 0){
                throw new Error(`Error code ${result.code}`);
            }
            if(!skip_msg && success_msg != null){
                {{ show_alert }} = true;
                {{ alert_header }} = success_msg;
                {{ alert_msg }} = result.output;
            }
            if (progress_component != null){
                progress_component = result.output;
            }
        } catch (error) {
            if(!skip_msg && fail_msg != null){
                {{ show_alert }} = true;
                {{ alert_header }} = fail_msg;
                {{ alert_msg }} = result.error;
            }
            console.error(error);
        }
        setBase_state({...base_state});
    };
    '''
        return Template(dedent(template)).render(task_progress=self.task_progress.full_name,
                                                 show_alert=self.base_state.show_alert.full_name,
                                                 alert_header=self.base_state.alert_header.full_name,
                                                 alert_msg=self.base_state.alert_msg.full_name)


def prepare_tab_button(title, tab_id, selected=False) -> rx.Component:
    """
    Creates a tab button component that can be used with a tab control.

    Args:
        title (str): The text to display on the tab button.
        tab_id (str): The ID of the corresponding tab panel that this button controls.

    Returns:
        rx.Component: A tab button component that can be added to the page.
    """
    output = el.li(
        el.button(
            title,
            class_name=add_class_tag(
                "inline-block p-4 border-b-2 rounded-t-lg", BUTTON_TEXT_CLS),
            id=f"{title.lower()}-tab",
            type="button",
            role="tab",
            custom_attrs={'data-tabs-target': f'#{tab_id}',
                          'aria-controls': f'{tab_id}',
                          'aria-selected': 'true' if selected else 'false'
                          }
        ),
        class_name="mr-2",
        role="presentation",
    )

    return output


def prepare_tab_content(content, tab_id) -> rx.Component:
    """
    Creates a tab content component that can be used with a tab control.

    Args:
        content (rx.Component): The content to display inside the tab panel.
        tab_id (str): The ID of the tab panel.

    Returns:
        rx.Component: A tab content component that can be added to the page.
    """
    output = el.div(
        content,
        class_name="hidden",
        id=f"{tab_id}",
        role="tabpanel",
        custom_attrs={'aria-labelledby': f'{tab_id}-tab'},
    )

    return output


js_getRefValues = BaseVar(name="getRefValues(refs)",
                          is_local=True, is_string=False)


def get_ref_value_fn(refs: List[str] = None, prefix=None) -> str:
    if refs is None:
        refs = "refs"
    else:
        refs = '[' + ",".join([f'''"ref_{ref}"''' for ref in refs]) + ']'
    if prefix is not None:
        func = f"getRefValues({refs}, 'ref_{prefix}')"
    else:
        func = f"getRefValues({refs})"
    return BaseVar(name=func, is_local=True, is_string=False)


class SpecialButton(rx.Button):
    # {execure_remote_command}
    special_on_click: str = None

    @classmethod
    def create(cls, *args, special_on_click: str = None, **kwargs) -> rx.Component:
        """Create a Bare component, with no tag.

        Args:
            contents: The contents of the component.

        Returns:
            The component.
        """
        output = super().create(*args, **kwargs)
        output.special_on_click = special_on_click
        return output

    def render(self) -> Dict:
        """Render the component.

        Returns:
            The dictionary for template of component.
        """
        tag = self._render()
        tag.props.pop('specialOnClick')

        output = dict(
            tag.add_props(
                # **self.event_triggers,
                key=self.key,
                sx=self.style,
                id=self.id,
                class_name=self.class_name,
                **self.custom_attrs,
            ).set(
                children=[child.render() for child in self.children],
                contents=str(tag.contents),
                props=tag.format_props(),
            ),
        )
        if self.special_on_click:
            special_on_click = ';'.join(self.special_on_click)
            output['props'].append(
                "onClick={() => { %s }}" % (special_on_click))

            # output['props'].append(f"onClick={self.special_on_click}")
        return output


specialButton = SpecialButton.create

# class MultiSelect(rx.Component):
#     library = "react-select"
#     tag = "MultiSelect"
#     is_default = True

#     is_multi: Var[bool] = False
#     default_value: Var[List[str]] = []

#     menu_position: Var[str] = "fixed"
#     menu_placement: Var[str] = "bottom"

#     options: Var[List[Dict[str,str]]] = []
