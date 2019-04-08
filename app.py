#!/usr/bin/env python3

from subprocess import call, Popen, PIPE
import json
import os
from os.path import expanduser
import re
import shutil
import sys
import getpass
from collections import OrderedDict


COMMAND, ENV, APP_TYPE, FRESH_INSTALL = None, None, None, False
RELEASE_TYPE, RELEASE_CANDIDATE_TYPE = None, None
# VERSIONS:
NODE_VERSION = "v10.15.3"
NG_CLI_VERSION = "7.3.8"
NVM_ALIAS = "ngGaePy3Sample"

# FILES and FOLDERS:
BACKEND_FOLDER_NAME = "server"
WEB_APP_FOLDER_NAME = "web-app"
PACKAGE_JSON_FILE = "package.json"
YAML_FILE = "app.yaml"


CURRENT_WORKING_DIRECTORY = os.getcwd()
BACKEND_PATH = f"{CURRENT_WORKING_DIRECTORY}/{BACKEND_FOLDER_NAME}"
VIRTUAL_ENV_PATH = f"{BACKEND_PATH}/env"
WEB_APP_PATH = f"{CURRENT_WORKING_DIRECTORY}/{WEB_APP_FOLDER_NAME}"
PACKAGE_JSON_PATH = f"{WEB_APP_PATH}/package.json"


class Colors:
    RED = "\033[01;31m"
    GREEN = "\033[01;32m"
    YELLOW = "\033[01;33m"
    BLUE = "\033[01;34m"
    PURPLE = "\033[01;35m"
    CYAN = "\033[01;36m"
    WHITE = "\033[01;37m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    NC = "\033[0m"  # No Color

    def __init__(self):
        pass

    @staticmethod
    def print_msg(msg, color):
        if not color:
            color = Colors.WHITE
        print(f"{color}{msg}{Colors.NC}")

    @staticmethod
    def print_error_with_icon(msg):
        print(f"{Colors.RED}✘{Colors.NC}{Colors.WHITE}{msg}{Colors.NC}")

    @staticmethod
    def print_success_with_icon(msg):
        print(f"{Colors.GREEN}✔{Colors.NC}{Colors.WHITE}{msg}{Colors.NC}")


class Utils:
    def __init__(self):
        pass

    @staticmethod
    def run_command(commands: str, abort: bool=True):
        """
        Run the command in subprocess
        :param commands: {str} Command to run.
        :param abort: {bool} flag set to exit if there is error. Default to true
        :return: Status of the command
        """
        try:
            return call(commands, shell=True)
        except Exception as exc:
            Colors.print_msg(f"Caught an error running the following command\n{commands}\nError > > > > :\n{exc}", Colors.RED)
            if abort:
                Colors.print_msg("ABORTING THE MISSION", Colors.RED)
                sys.exit(3)

    @staticmethod
    def show_help():
        """
        Display help message
        """
        with open("help.txt") as help_content:
            help_msg = help_content.read()
        Colors.print_msg(help_msg, Colors.CYAN)
        sys.exit(0)

    @staticmethod
    def get_command_output(commands: list, abort: bool = False):
        """
        Run the command and get output
        :param commands: {list} arguments of command to execute
        :param abort: {bool} flag set to exit if there is error. Default to false
        :return: {str}
        """
        proc = Popen(commands, stdout=PIPE, stderr=PIPE)
        output, error = proc.communicate()
        if error:
            Colors.print_msg(f"Caught an error or warning running the following command\n{commands}\nError/Warning > > > > :\n{error.decode('ascii')}", Colors.YELLOW)
            if abort:
                Colors.print_msg("ABORTING THE MISSION", Colors.YELLOW)
                sys.exit(2)
        return output.decode('ascii').strip("\n")

    @staticmethod
    def print_error_show_help(msg):
        """
        Print error message and show help message/
        :param msg: {str}
        """
        Colors.print_msg(msg, Colors.RED)
        Utils.show_help()

    @staticmethod
    def is_pip_package_installed(package_name) -> bool:
        """
        Check if the pip package is installed
        :param package_name: {str}
        :return: {bool}
        """
        print(package_name)
        pip_list = json.loads(Utils.get_command_output(["pip", "list", "--format=json"]))
        print(pip_list)
        is_package_installed = (item for item in pip_list if item["name"] == package_name)
        return not not is_package_installed


# TODO: Need to test this
try:
    import yaml
    Colors.print_success_with_icon("PyYaml is installed globally")
except ImportError as e:
    Colors.print_error_with_icon(f"PyYAML lib not installed. \nError > > > >:\n{e}\n\nInstalling now!")
    Utils.run_command("pip3 install pyyaml")
    Colors.print_success_with_icon("Successfully installed PyYAML globally")
    import yaml


class Environment:
    def __init__(self):
        self.is_linux = os.name == "posix"
        self.is_windows = os.name == "nt"
        self.deploy_version = None
        self.gcp_project_id = None
        self.get_gcp_project_id()
        self.get_app_version()
        print(self.__dict__)

    def get_gcp_project_id(self):
        """
        Get GCP project id from app.yaml
        """
        with open(f"{BACKEND_FOLDER_NAME}/{YAML_FILE}", 'r') as stream:
            try:
                yaml_data = yaml.load(stream, yaml.FullLoader)
                self.gcp_project_id = yaml_data["env_variables"]["PROD_APP_ID"]
            except yaml.YAMLError as exc:
                Colors.print_msg(f"Caught an error when reading app.yaml to get gcp project id. ABORTING THE MISSION! \n Error >>>>\n{exc}", Colors.RED)
                sys.exit(2)

    def get_app_version(self):
        """
        Get the app version from package.json
        """
        file_location = f"{WEB_APP_FOLDER_NAME}/{PACKAGE_JSON_FILE}"
        with open(file_location) as json_content:
            self.deploy_version = json.load(json_content)["version"].replace(".", "-")
        username = getpass.getuser()
        self.deploy_version = f"{self.deploy_version}-{username}"

    def set_deploy_version(self, version: str):
        """
        If the version is passed as argument, update it accordingly
        :param version: {str}
        """
        self.deploy_version = version


class VirtualEnv:
    def __init__(self):
        pass

    @staticmethod
    def check_installed_globally():
        """
        Check if virtual environment is installed globally. If not, install it
        """
        is_virtual_env_installed = Utils.is_pip_package_installed("virtualenv")
        if is_virtual_env_installed:
            Colors.print_success_with_icon("Virtual environment package is installed")
        else:
            Colors.print_msg("Virtual environment package is not installed. Installing it.", Colors.YELLOW)
            # TODO: NEED TO TEST THIS
            if ENV.is_windows:
                Utils.run_command("python3 -m pip install --user virtualenv")
            else:
                Utils.run_command("py -m pip install --user virtualenv")
            Colors.print_success_with_icon("Successfully installed virtual environment globally")

    @staticmethod
    def run_command(command: str):
        """
        Run backend command that needs virtual env activated
        :param command: {str}
        """
        Utils.run_command(f". activate_virtual_env.sh; {command}")


class Server:
    def __init__(self):
        pass

    @staticmethod
    def validate_deploy_version():
        """
        Validate the deploy version
        """
        # global ENV
        possible_version_pattern = re.compile(r"[a-zA-Z0-9-]")
        if not possible_version_pattern.match(ENV.deploy_version):
            Colors.print_msg("Invalid version for deploy. Version should include alphanumeric character and hyphen only", Colors.RED)
            sys.exit(1)
        else:
            Colors.print_success_with_icon(f"Version pattern: '{ENV.deploy_version}' is valid")

    @staticmethod
    def set_gcp_project():
        """
        Set GCP project id locally
        """
        gcp_project_id = ENV.gcp_project_id
        Colors.print_msg(f"Setting GCP project id to {gcp_project_id}", Colors.BLUE)
        Utils.run_command(f"gcloud config set project {gcp_project_id}")
        output = Utils.get_command_output(["gcloud", "config", "get-value", "project"])
        Colors.print_msg(f"GCP project id set to {output}", Colors.BLUE)

    @staticmethod
    def check_gcloud_sdk_installed():
        """
        Check GCloud SDK is installed
        """
        output = Utils.get_command_output(["which", "gcloud"])
        # For windows
        # output = get_command_output(["where", "gcloud"])
        if not output:
            Colors.print_error_with_icon("GCloud SDK not installed.")
            Utils.print_error_show_help("Please install GCloud SDK before continuing")
        else:
            Colors.print_success_with_icon("GCloud SDK is installed.")

    @staticmethod
    def install_dependencies():
        """
        Install server dependencies
        """
        Colors.print_msg("Installing backend dependencies", Colors.BLUE)
        VirtualEnv.run_command(f"pip install -r {BACKEND_FOLDER_NAME}/requirements.txt --upgrade --no-cache-dir")

    @staticmethod
    def deploy():
        """
        Build and deploy app to server
        """
        Server.check_gcloud_sdk_installed()
        Server.validate_deploy_version()
        Server.set_gcp_project()
        Angular.build()
        os.chdir(BACKEND_PATH)
        Utils.run_command(f"gcloud app deploy app.yaml --version={ENV.deploy_version} --no-promote")

    @staticmethod
    def check_virtual_env_for_project():
        """
        Check if the virtualenv is installed for the project, if not, install it
        """
        if not os.path.isdir(VIRTUAL_ENV_PATH):
            Colors.print_error_with_icon("Virtual Environment not setup for this project. Setting up now")
            if ENV.is_windows:
                Utils.run_command(f"py -m virtualenv {VIRTUAL_ENV_PATH}")
            else:
                Utils.run_command(f"python3 -m virtualenv {VIRTUAL_ENV_PATH}")
            Colors.print_success_with_icon("Virtual Environment is now created for this project.")
        else:
            Colors.print_success_with_icon("Virtual Environment is setup for this project.")

    @staticmethod
    def run_locally():
        """
        Run server locally
        """
        print(f"{VIRTUAL_ENV_PATH}/bin/activate")
        if ENV.is_windows:
            # run_command(".\env\Scripts\activate")
            Colors.print_msg("The windows environment is not configured yet.", Colors.RED)
            sys.exit(3)
        else:
            VirtualEnv.run_command("python3 server/main.py")

    @staticmethod
    def setup_locally():
        """
        Setup server locally
        """
        Colors.print_msg("Setting up backend.", Colors.BLUE)
        Server.check_gcloud_sdk_installed()
        VirtualEnv.check_installed_globally()
        Server.set_gcp_project()
        Server.check_virtual_env_for_project()
        Server.install_dependencies()


class Node:
    def __init__(self):
        pass

    @staticmethod
    def install_globally():
        """
        Install node version for the project and install all the dependencies globally
        Also set NVM alias for the project
        """
        # global NODE_VERSION, NVM_ALIAS, NG_CLI_VERSION
        Nvm.run_command(node_commands=[f"nvm install {NODE_VERSION}", f"nvm alias {NVM_ALIAS} {NODE_VERSION}"], use_nvm=False)
        Colors.print_msg("Installing typescript, angular/cli", Colors.PURPLE)
        Nvm.run_command([f"npm i -g @angular/cli@{NG_CLI_VERSION} typescript"], use_nvm=True)

    @staticmethod
    def check_verison():
        """
        Check node version. If version doesn't match, install the correct version
        """
        output = Utils.get_command_output(["node", "-v"])
        if output != NODE_VERSION:
            try:
                # Check if node is installed via nvm
                Nvm.check_n_install_nvm()
                Nvm.check_alias_exist()
            except Exception as ex:
                arrow = " >" * 5
                Colors.print_msg(f"Unable to use {NODE_VERSION} Node. Installing it now. \n\nError{arrow}:\n{ex}", Colors.YELLOW)
                Node.install_globally()
            Colors.print_success_with_icon(f"Node {NODE_VERSION} is installed and using")

    @staticmethod
    def check_n_install():
        """
        Check if Node JS is installed or not. If not, install it
        """
        node_path = Utils.get_command_output(["which", "node"])
        if not node_path:
            Colors.print_error_with_icon("Node is not installed.")
            Nvm.check_n_install_nvm()
        # Check node version
        Node.check_verison()


class Nvm:
    def __init__(self):
        pass

    @staticmethod
    def run_command(node_commands: list = None, use_nvm: bool = True):
        """
        When running node version via nvm, python environment doesn't know where nvm is installed. So it throws error.
        Therefore, source into bash_profile to activate nvm, used the correct version of nvm and then run the command
        :param node_commands: {list} list of commands to run at once
        :param use_nvm: {boolean} defaults to True. If you don't need to use the nvm. For example you don't need to use it when installing node version
        :return: {int} Status. Usually 0 if success
        """
        home_path = expanduser("~")
        bash_file_name = ".bash_profile"
        bash_exists = os.path.isfile(f"{home_path}/{bash_file_name}")
        if not bash_exists:
            bash_file_name = ".zshrc"
        command_to_run = f"source {home_path}/{bash_file_name}; "
        if use_nvm:
            command_to_run += f"nvm use {NVM_ALIAS}; "
        if node_commands:
            command_to_run += "node -v; "
            command_to_run += "; ".join(node_commands)
        result = Utils.run_command(command_to_run)
        return result

    @staticmethod
    def check_n_install_nvm():
        """
        Check if Node version manager is installed. If not, install it
        """
        status = Nvm.run_command(["nvm --version"])
        print("here > > ", status)
        if status != 0:
            Colors.print_msg("Node Version Manager (NVM) is not installed.", Colors.YELLOW)
            count = 1
            resp = None
            while count < 4 and (not resp or resp.lower() not in ["y", "n"]):
                resp = input("Do you want to install Node Version Manager (NVM)? (Y/n)")
                if count > 1:
                    print("Please enter \"Y\" or \"n\"")
                count += 1
            if count == 4:
                Colors.print_msg("Failed to install Node. Please run the command again or install node before continuing.", Colors.RED)
                sys.exit(3)
            elif resp.lower() == "n":
                Colors.print_msg("Aborting ionic app setup.", Colors.RED)
                sys.exit(3)
            else:
                Utils.run_command("curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.34.0/install.sh | bash")
                Colors.print_success_with_icon("NVM installed")
        else:
            Colors.print_success_with_icon("Node Version Manager (NVM) is installed.")

    @staticmethod
    def check_alias_exist():
        """
        Check if the NVM alias for the project is set, if not set it
        """
        # global NVM_ALIAS
        status = Nvm.run_command()
        if status != 0:
            # Check node version installed in NVM
            node_app_version_installed_status = Nvm.run_command([f"nvm ls {NODE_VERSION}"], use_nvm=False)
            if node_app_version_installed_status != 0:
                # Installing Node version
                Colors.print_error_with_icon(f"Node version {NODE_VERSION} not installed. Installing now.")
                Node.install_globally()
            else:
                Colors.print_success_with_icon(f"Node version {NODE_VERSION} exists.")
            nvm_alias_status = Nvm.run_command([f"nvm ls {NVM_ALIAS}"], use_nvm=False)
            if nvm_alias_status != 0:
                # Installing Node version
                Colors.print_error_with_icon(f"NVM alias {NVM_ALIAS} not setup. Adding the alias now.")
                Nvm.run_command([f"nvm alias {NVM_ALIAS} {NODE_VERSION}"])
        else:
            Colors.print_success_with_icon(f"NVM alias {NVM_ALIAS} exists.")


class Angular:
    def __init(self):
        pass

    @staticmethod
    def get_package_json_content():
        """
        Get the package.json contain preserving the order format
        :return: {OrderedDict}
        """
        with open(PACKAGE_JSON_PATH, "r") as json_file:
            data = json.load(json_file, object_pairs_hook=OrderedDict)
        return data

    @staticmethod
    def update_version_package_json():
        """
        Update app version in package.json file
        Note: The file format may not be same once the file re-written
        """
        # global ENV
        pkg_content = Angular.get_package_json_content()
        pkg_content["version"] = ENV.version
        with open(PACKAGE_JSON_PATH, "w") as outfile:
            # To remove the trailing whitespace and add a space after colon
            json.dump(pkg_content, outfile, indent=2, separators=(",", ": "))

    @staticmethod
    def install_dependencies():
        """
        Install Angular app dependencies
        """
        os.chdir(WEB_APP_PATH)
        Nvm.check_alias_exist()
        if FRESH_INSTALL:
            Colors.print_msg("Deleting node_modules and package-lock.json for fresh install", Colors.PURPLE)
            if os.path.exists("node_modules"):
                shutil.rmtree("node_modules")
            if os.path.exists("package-lock.json"):
                os.remove("package-lock.json")
        Colors.print_msg("Installing NPM dependencies for the project.", Colors.BLUE)
        Nvm.run_command(["npm i"])

    @staticmethod
    def setup_locally():
        """
        Setup Angular app locally
        """
        Colors.print_msg("Setting up Angular app.", Colors.PURPLE)
        Node.check_n_install()
        Angular.install_dependencies()

    @staticmethod
    def run_locally():
        """
        Run Angular app locally
        """
        Colors.print_msg("Running  Angular app.", Colors.PURPLE)
        os.chdir(WEB_APP_PATH)
        Nvm.run_command(["npm start"])

    @staticmethod
    def build():
        """
        Build Angular for deploying
        """
        Colors.print_msg("Building  Angular app.", Colors.PURPLE)
        os.chdir(WEB_APP_PATH)
        Nvm.run_command(["ng build --prod"])


def parse_args():
    """
    Parse the arguments passed via command line
    """
    global COMMAND, FRESH_INSTALL, APP_TYPE, ENV, RELEASE_TYPE, RELEASE_CANDIDATE_TYPE
    possible_version_format = re.compile(r"version=[a-zA-Z\d-]*")
    skip_next_iter = False
    for index, arg in enumerate(all_args):
        if skip_next_iter:
            # Need this if passing version as `version 0-0-2-as`
            skip_next_iter = False
            continue
        elif arg in ["-d", "deploy", "-s", "setup", "-h", "help", "-r", "run", "-b", "build"]:
            if COMMAND:
                Utils.print_error_show_help(f"More than one command provide {COMMAND} and {arg}")
            COMMAND = arg
        elif arg in ["-f", "fresh"]:
            FRESH_INSTALL = True
        elif arg in ["google-app-engine", "gae", "web", "ng", "angular"]:
            APP_TYPE = arg
        elif arg in ["-v", "version"]:
            version = all_args[index + 1]
            skip_next_iter = True
            if not version:
                Utils.print_error_show_help("Missing version")
            ENV.set_deploy_version(version)
        elif possible_version_format.match(arg):
            version = arg[arg.index("=") + 1:]
            if not version:
                Utils.print_error_show_help("Missing version")
            ENV.set_deploy_version(version)
        elif arg in ["major", "minor", "patch"]:
            RELEASE_TYPE = arg
        elif arg in ["rc", "alpha", "beta"]:
            RELEASE_CANDIDATE_TYPE = arg
        else:
            Utils.print_error_show_help(f"Invalid Command / Argument: {arg}\nSee help")


def execute_command():
    """
    Execute the command
    """
    global APP_TYPE, COMMAND, NODE_VERSION
    is_ng = APP_TYPE in ["web", "ng", "angular"]
    is_gae = APP_TYPE in ["gae", "google-app-engine"]
    if COMMAND in ["-s", "setup"]:
        if is_gae:
            Server.setup_locally()
        elif is_ng:
            Angular.setup_locally()
        else:
            # Do everything of GAE and Angular
            Server.setup_locally()
            Angular.setup_locally()
    elif COMMAND in ["-d", "deploy"]:
        Server.deploy()
    elif COMMAND in ["-r", "run"]:
        if is_ng:
            Angular.run_locally()
        elif is_gae:
            Server.run_locally()
        else:
            # Start two processes
            pass
    elif COMMAND in ["-b", "build"]:
        Angular.build()
    elif COMMAND in ["-h", "help"]:
        Utils.show_help()


if __name__ == "__main__":
    script_name = sys.argv[0]
    all_args = sys.argv[1:]
    Colors.print_msg(f"Running {script_name}.", Colors.BLUE)
    if len(all_args) == 0:
        Utils.print_error_show_help("Missing commands and/or arguments")
    ENV = Environment()
    if not ENV.is_linux:
        Colors.print_msg(f"THIS SCRIPT HASN'T BEEN TESTED IN {os.name.upper()} OPERATING SYSTEM!!!", Colors.YELLOW)
    parse_args()
    execute_command()

# TODO:
"""
[ ] - Run Angular and Server locally at once
[ ] - Update package.json version and also update/add to app.yaml
[ ] - Update version based on major, minor, patch
"""