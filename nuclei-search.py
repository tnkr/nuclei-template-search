#! /opt/homebrew/bin/python3

import argparse
import os
import yaml
from colorama import init, Fore, Style
from pygments import highlight
from pygments.lexers import YamlLexer
from pygments.formatters import TerminalFormatter

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".nuclei_search_config.yaml")

def get_template_folder():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            if "template_folder" in config and os.path.exists(config["template_folder"]):
                return config["template_folder"]

    default_template_folder = input("Enter the path to the nuclei-templates folder: ")
    default_template_folder = os.path.expanduser(default_template_folder)

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        yaml.dump({"template_folder": default_template_folder}, f)

    return default_template_folder

def search_templates(search_term, template_folder):
    results = []
    for root, _, files in os.walk(template_folder):
        for file in files:
            if file.endswith(".yaml"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if search_term.lower() in content.lower():
                        results.append(file_path)
    return results

def display_results(results):
    for i, file_path in enumerate(results, 1):
        components = file_path.split(os.sep)
        indent = " " * (len(components) - 1)
        file_name = components[-1]

        # Add color to the template path for better visibility
        colored_path = Style.BRIGHT + Fore.BLUE + os.sep.join(components[:-1]) + os.sep + Style.RESET_ALL

        print(f"{i}. {indent}{colored_path}{Fore.GREEN}{file_name}{Style.RESET_ALL}")

if __name__ == "__main__":
    init(autoreset=True)  # Initialize colorama

    parser = argparse.ArgumentParser(description="Search templates in the nuclei-templates repository.")
    parser.add_argument("search_term", help="Search term to find templates.")
    parser.add_argument("--template-folder", help="Local folder containing the template files.")
    args = parser.parse_args()

    template_folder = args.template_folder or get_template_folder()

    if not os.path.exists(template_folder):
        print(f"Template folder '{template_folder}' does not exist.")
        exit(1)

    print(f"\nSearching for templates with the term '{args.search_term}'...\n")
    results = search_templates(args.search_term.lower(), template_folder)

    if results:
        display_results(results)

        while True:
            try:
                selected = int(input("\nEnter the number of the template to view (or 0 to exit): "))
                if selected == 0:
                    break
                elif 1 <= selected <= len(results):
                    selected_template = results[selected - 1]
                    with open(selected_template, "r", encoding="utf-8") as f:
                        template_content = f.read()
                        yaml_content = yaml.safe_load(template_content)

                    # Use Pygments to apply syntax highlighting for YAML output
                    formatted_yaml = highlight(
                        yaml.dump(yaml_content, default_flow_style=False),
                        YamlLexer(),
                        TerminalFormatter(),
                    )

                    print(f"\nContent of template '{selected_template}':\n")
                    print(formatted_yaml)
                else:
                    print("Invalid number. Please enter a valid number or 0 to exit.")
            except ValueError:
                print("Invalid input. Please enter a number or 0 to exit.")
    else:
        print(f"No templates found with the term '{args.search_term}'.")
