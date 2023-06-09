import os
from enum import Enum
from jinja2 import Template
from pynecone.vars import BaseVar

bool_t = lambda x: x.lower() in ['true', 'yes', '1']

WEB_HOSTING = bool_t(os.environ.get("WEB_HOSTING", '0'))

prefix_to_watch = ("env_", "extra_", "add_", "gpu_list")

FREE_GPU = ['Free-GPU']
PRO_GPU = ["A4000", "P6000", "P5000", "RTX5000", "RTX4000", "P4000"]
PRO_FREE_GPU = ['Free-A4000', 'Free-RTX5000',
                'Free-P5000', 'Free-RTX4000', 'Free-P4000']
GROWTH_GPU = ['A100-80G', 'A100', 'A6000', 'A5000', 'V100-32G', 'V100']
GROWTH_FREE_GPU = ['Free-A100-80G', 'Free-A6000', 'Free-A5000', ]

GPU_TIER = [("Free Tier", FREE_GPU), ("Pro Tier", PRO_FREE_GPU +
                                      PRO_GPU), ("Growth Tier", GROWTH_FREE_GPU + GROWTH_GPU)]
ALL_GPU = FREE_GPU + PRO_GPU + PRO_FREE_GPU + GROWTH_GPU + GROWTH_FREE_GPU

REFRESH_RATE = 1
PAPERSPACE_START_RATE = 5
PAPERSPACE_TIMEOUT = 60 * 30    # 30 minutes
PAPERSPACE_DEFAULT_COMMAND = "bash entry.sh >> /tmp/run.log & jupyter lab --allow-root --ip=0.0.0.0 --no-browser --ServerApp.trust_xheaders=True --ServerApp.disable_check_xsrf=False --ServerApp.allow_remote_access=True --ServerApp.allow_origin='*' --ServerApp.allow_credentials=True"
PAPERSPACE_DEFAULT_CONTAINER = "paperspace/gradient-base:pt112-tf29-jax0317-py39-20230125"

BUTTON_TEXT_CLS = "text-gray-900 dark:text-white"
HEADING_CLASS = "mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-gray-300"
TEXT_COLOR_CLASS = "text-gray-700 dark:text-gray-300"
BUTTON_CLS = "text-gray-900 bg-white border border-gray-300 focus:outline-none hover:bg-gray-100 focus:ring-4 focus:ring-gray-200 font-medium rounded-full text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-gray-800 dark:text-white dark:border-gray-600 dark:hover:bg-gray-700 dark:hover:border-gray-600 dark:focus:ring-gray-700"
NORMAL_BUTTON_CLS = "text-gray-900 bg-white border border-gray-300 focus:outline-none hover:bg-gray-100 focus:ring-4 focus:ring-gray-200 font-medium rounded-lg text-sm px-5 py-2.5 dark:bg-gray-800 dark:text-white dark:border-white dark:hover:bg-gray-700 dark:hover:border-gray-600 dark:focus:ring-gray-700"
NORMAL_TOOLTIP_CLS = "absolute z-10 invisible inline-block px-3 py-2 text-sm font-medium text-white transition-opacity duration-300 bg-gray-900 rounded-lg shadow-sm opacity-0 tooltip dark:bg-gray-700"
ICON_PROPS = '''class="w-6 h-6 mb-1 text-gray-500 dark:text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-500" fill="currentColor" viewbox="0 0 20 20'''
SELECT_OPTION_CLS = "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"

ACCORDION_BUTTON_CLS = "flex items-center justify-between w-full font-medium text-left text-gray-500 focus:ring-4 focus:ring-gray-200 dark:focus:ring-gray-800 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800"

icons = {
    "Home": '''<svg aria-hidden="true" class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
    <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"></path>
    </svg>''',
    "Paperspace": f'''<svg aria-hidden="true" {ICON_PROPS} xmlns="http://www.w3.org/2000/svg">
  <path d="M14 6H6v8h8V6z"></path>
  <path clip-rule="evenodd" d="M9.25 3V1.75a.75.75 0 011.5 0V3h1.5V1.75a.75.75 0 011.5 0V3h.5A2.75 2.75 0 0117 5.75v.5h1.25a.75.75 0 010 1.5H17v1.5h1.25a.75.75 0 010 1.5H17v1.5h1.25a.75.75 0 010 1.5H17v.5A2.75 2.75 0 0114.25 17h-.5v1.25a.75.75 0 01-1.5 0V17h-1.5v1.25a.75.75 0 01-1.5 0V17h-1.5v1.25a.75.75 0 01-1.5 0V17h-.5A2.75 2.75 0 013 14.25v-.5H1.75a.75.75 0 010-1.5H3v-1.5H1.75a.75.75 0 010-1.5H3v-1.5H1.75a.75.75 0 010-1.5H3v-.5A2.75 2.75 0 015.75 3h.5V1.75a.75.75 0 011.5 0V3h1.5zM4.5 5.75c0-.69.56-1.25 1.25-1.25h8.5c.69 0 1.25.56 1.25 1.25v8.5c0 .69-.56 1.25-1.25 1.25h-8.5c-.69 0-1.25-.56-1.25-1.25v-8.5z" fill-rule="evenodd"></path>
</svg>'''
}
paperspace_timeout_options = ["1", "2", "3", "4", "5", "6"]
PAPERSPACE_MONITOR_INTERVAL = 5

STAGE_BASE_TEMPLATE = Template('''
### Setting up {{ title }} ###
{% if download_model %}
### Downloading Model for {{ title }} ###
{% endif %}
### Starting {{ title }} ###
''')
FASTCHAT_MODELS = ["vicuna-13b", "vicuna-7b", "chatglm-6b"]
TEXTGEN_MODELS = [ "vicuna-13B-1.1-GPTQ-4bit-128g",
                   "vicuna-AlekseyKorshuk-7B-GPTQ-4bit-128g", 
                   "vicuna-13B-1.1", "vicuna-7B-1.1"
                ]

class Page(Enum):
    main = 0
    control_panel = 1
