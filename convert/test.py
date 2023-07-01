
from reflex.vars import BaseVar

el.Button.add_field(BaseVar(name='data-tabs-target'), default_value=None)
el.Div.add_field(BaseVar(name='aria-labelledby'), default_value=None)
el.Button.add_field(BaseVar(name='aria-selected'), default_value=None)
el.Ul.add_field(BaseVar(name='data-tabs-toggle'), default_value=None)
el.Button.add_field(BaseVar(name='aria-controls'), default_value=None)

div = el.Div.create
button = el.Button.create
ul = el.Ul.create

output = el.div(
    c := el.ul(
        el.li(
            d := el.button(
                "Profile",
                class_name="inline-block p-4 border-b-2 rounded-t-lg",
                id="profile-tab",
                type="button",
                role="tab",
            ),
            class_name="mr-2",
            role="presentation",
        ),
        class_name="flex flex-wrap -mb-px text-sm font-medium text-center",
        id="myTab",
        role="tablist",
    ),
    class_name="mb-4 border-b border-gray-200 dark:border-gray-700",
),
el.div(
    e := el.div(
        el.p(
            "This is some placeholder content the",
            el.strong(
                "Profile tab's associated content",
                class_name="font-medium text-gray-800 dark:text-white",
            ),
            ". Clicking another tab will toggle the visibility of this one for the next. The tab JavaScript swaps classes to control the content visibility and styling.",
            class_name="text-sm text-gray-500 dark:text-gray-400",
        ),
        class_name="hidden p-4 rounded-lg bg-gray-50 dark:bg-gray-800",
        id="profile",
        role="tabpanel",
    ),
    id="myTabContent",
)

setattr(c, 'data-tabs-toggle', '#myTabContent')
setattr(d, 'data-tabs-target', '#profile')
setattr(d, 'aria-controls', 'profile')
setattr(d, 'aria-selected', 'false')
setattr(e, 'aria-labelledby', 'profile-tab')
