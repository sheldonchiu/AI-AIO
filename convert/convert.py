# pip install autopep8 bs4
import autopep8
import string
import itertools
from pynecone import el
from pynecone.el.constants.pynecone import attr_to_prop
from pynecone.el.constants.html import ELEMENTS
from bs4 import BeautifulSoup
import argparse

# Define a generator function for generating variable names
def generate_var_name():
    # Get all lowercase letters of the English alphabet
    letters = string.ascii_lowercase
    # Loop over increasing lengths of combinations
    for length in range(1, len(letters) + 1):
        # Generate combinations of letters
        for combination in itertools.product(letters, repeat=length):
            # Convert combination to string and yield as next value
            output = "".join(combination)
            # check if generated variable name is defined in pynecone elements
            if output not in ELEMENTS:
                yield "".join(combination)
var_generator = generate_var_name()

missing_attr = {}
# Define a function for processing each HTML tag
def process_tag(tag, output, list_of_elements):
    if tag.name == '[document]' or tag.name in list_of_elements:
        props = ""
        missing_attr_temp = {}
        for attr in tag.attrs:
            # convert html tag to possible pynecone tag
            py_attr = attr_to_prop(attr)
            # check if attrs is already defined in pynecone
            if not hasattr(getattr(el, tag.name)(), py_attr):
                missing_attr_temp[attr] = tag[attr]
                continue
            if type(tag[attr]) == list:
                props += f'{py_attr} = "{" ".join(tag[attr])}",\n'
            else:
                props += f'{py_attr} = "{tag[attr]}",\n'
        if len(missing_attr_temp) > 0:
            # Generate a unique variable name for the new HTML element
            var_name = next(var_generator)
            missing_attr[(tag.name, var_name)] = missing_attr_temp
            var_name = f"{var_name} := el.{tag.name}"
        else:
            var_name = "el." + tag.name

        if tag.name != '[document]':
            output += var_name + "(\n"
        # if tag.string is not None:
        #     output += f'"{tag.string}",\n'
        # Recursively process each child tag
        for child in tag.children:
            if child.name is None and child != '\n':
                output += f'"{child.strip()}",\n'
            if child.name is not None:
                output = process_tag(child, output, list_of_elements)
        output += props
        # Add closing parentheses to the output string
        if tag.name != '[document]':
            output += "),\n"
    else:
        # use raw html if tag is not defined in pynecone
        output += f"pc.html('''{tag}'''),\n"

    # Return the updated output string
    return output

def main(args):
    with open(args.input, 'r') as f:
        html_content = f.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    imports = '''
    from pynecone.vars import BaseVar

    '''
    output = imports
    list_of_elements = [
        e for e in ELEMENTS if e not in args.skip_element.split(',')]
    html_parse = process_tag(soup, "", list_of_elements)
    if html_parse.endswith(",\n"):
        html_parse = html_parse[:-2]

    output_add_field = []
    output_var_define = []
    output_var_set = ""
    for key, value in missing_attr.items():
        component_class = f"el.{key[0].capitalize()}"
        output_add_field.extend(
            [f"{component_class}.add_field(BaseVar(name='{k}'), default_value=None)" for k in value.keys()])
        output_var_define.append(f"{key[0]} = {component_class}.create")
        for key1, value1 in value.items():
            # TODO: type cast for value1 ?
            output_var_set += f"setattr({key[1]}, '{key1}', '{value1}')\n"

    output += '\n'.join(set(output_add_field)) + '\n\n'
    output += '\n'.join(set(output_var_define)) + '\n\n'
    output += f"output = {html_parse}\n\n"
    output += output_var_set

    output = autopep8.fix_code(output)
    with open(args.output, 'w') as f:
        f.write(output)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="path to html file")
    parser.add_argument("--output", type=str, default="output.py", help="path to output file")
    parser.add_argument("--skip_element", type=str, default="", help="list of elements to remain in html and embed using pc.html, separate by comma")
    args = parser.parse_args()

    main(args)
