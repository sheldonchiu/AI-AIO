from app.utils.constants import *
from app.utils.components import prepare_tab_button, prepare_tab_content
import reflex as rx
from reflex import el
from app.state.paperspace import PaperspaceState

def create_navbar() -> rx.Component:
    output = el.nav(
        el.div(
            el.a(
                rx.image(src="/icon.png",
                         width="60px",
                         height="auto"
                         ),
                el.span(
                    "PaperSpace AI AIO",
                    class_name="pl-4 self-center text-xl font-semibold whitespace-nowrap dark:text-white",
                ),
                # href="https://flowbite.com/",
                class_name="flex items-center",
            ),
            el.button(
                el.span(
                    "Open main menu",
                    class_name="sr-only",
                ),
                rx.html('''<svg aria-hidden='true' class='w-6 h-6' fill='currentColor' viewbox='0 0 20 20' xmlns='http://www.w3.org/2000/svg'><path clip-rule='evenodd' d='M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z' fill-rule='evenodd'></path></svg>'''),
                type="button",
                class_name="inline-flex items-center p-2 ml-3 text-sm text-gray-500 rounded-lg md:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:text-gray-400 dark:hover:bg-gray-700 dark:focus:ring-gray-600",
                custom_attrs={'data-collapse-toggle': 'navbar-default',
                              'aria-controls': 'navbar-default',
                              'aria-expanded': 'false'
                              }
            ),
            el.div(
            el.ul(
                    prepare_tab_button("Main", "main-content", selected=True),
                    prepare_tab_button("Control Panel", "control-panel-content", selected=False),
                    el.li(
                        el.div(
                            el.button(
                                rx.html('''<svg class='hidden w-5 h-5' fill='currentColor' id='theme-toggle-dark-icon' viewbox='0 0 20 20' xmlns='http://www.w3.org/2000/svg'><path d='M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z'></path></svg>'''),
                                rx.html('''<svg class='hidden w-5 h-5' fill='currentColor' id='theme-toggle-light-icon' viewbox='0 0 20 20' xmlns='http://www.w3.org/2000/svg'><path clip-rule='evenodd' d='M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z' fill-rule='evenodd'></path></svg>'''),
                                id="theme-toggle",
                                type="button",
                                class_name="rounded-full font-medium text-gray-500 dark:text-gray-400 hover:bg-blue-700 hover:text-white dark:hover:text-white focus:outline-none focus:ring-4 focus:ring-gray-200 dark:focus:ring-gray-700 text-sm p-2.5",
                            ),
                            class_name="flex items-center justify-center",
                        ),
                    ),
                    class_name="flex flex-col p-4 mt-4 border border-gray-100 rounded-lg md:flex-row md:pb-2 md:space-x-8 md:mt-0 md:text-sm md:font-medium md:border-0 dark:border-gray-700",
                    custom_attrs={'data-tabs-toggle': '#main-display'},
                ),
                class_name="hidden w-full md:block md:w-auto",
                id="navbar-default",
                role="presentation",
            ),
            class_name="container flex flex-wrap items-center justify-between mx-auto",
        ),
        class_name="border-gray-200 px-2 sm:px-4 py-2.5 rounded",
    )
    return output
