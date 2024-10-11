import os
import json
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path

import click
from click import echo
from click import secho
from getpass import getpass

# Constants for configuration files
CONFIG_FILE = Path("cconfig.json")
SECRETS_FILE = Path("secrets.json")
WORKFLOWS_FILE = Path("workflows.json")

# Strategy Pattern Base Class
class Strategy(ABC):
    @abstractmethod
    def execute(self, **kwargs):
        pass

# Concrete Strategy for Adding a Secret
class AddSecretStrategy(Strategy):
    def execute(self, **kwargs):
        repo = kwargs.get('repo')
        secret_name = kwargs.get('secret_name')
        secret_value = kwargs.get('secret_value')
        token = kwargs.get('token')

        add_secret(repo, secret_name, secret_value, token)
        save_secret_locally(secret_name, secret_value)

# Concrete Strategy for Adding a Workflow
class AddWorkflowStrategy(Strategy):
    def execute(self, **kwargs):
        repo = kwargs.get('repo')
        workflow_name = kwargs.get('workflow_name')
        workflow_content = kwargs.get('workflow_content')
        token = kwargs.get('token')

        add_workflow(repo, workflow_name, workflow_content, token)

# Concrete Strategy for Storing Configuration
class StoreConfigStrategy(Strategy):
    def execute(self, **kwargs):
        config_key = kwargs.get('config_key')
        config_value = kwargs.get('config_value')

        store_config(config_key, config_value)

# Concrete Strategy for Removing a Secret
class RemoveSecretStrategy(Strategy):
    def execute(self, **kwargs):
        repo = kwargs.get('repo')
        secret_name = kwargs.get('secret_name')
        token = kwargs.get('token')

        remove_secret(repo, secret_name, token)
        delete_secret_locally(secret_name)

# Function to Add Secret Using GitHub CLI
def add_secret(repo, secret_name, secret_value, token):
    secho(f"Adding secret '{secret_name}' to repo '{repo}'...", fg='green')
    command = [
        "gh", "secret", "set", secret_name,
        "--repo", repo,
        "--body", secret_value
    ]
    env = os.environ.copy()
    env['GITHUB_TOKEN'] = token

    try:
        subprocess.run(command, check=True, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        secho(f"Secret '{secret_name}' added to repository '{repo}' successfully.", fg='green')
    except subprocess.CalledProcessError as e:
        secho(f"Error adding secret: {e.stderr.decode().strip()}", fg='red')

# Function to Remove Secret Using GitHub CLI
def remove_secret(repo, secret_name, token):
    secho(f"Removing secret '{secret_name}' from repo '{repo}'...", fg='yellow')
    command = [
        "gh", "secret", "remove", secret_name,
        "--repo", repo,
        "-y"  # Automatically confirm removal
    ]
    env = os.environ.copy()
    env['GITHUB_TOKEN'] = token

    try:
        subprocess.run(command, check=True, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        secho(f"Secret '{secret_name}' removed from repository '{repo}' successfully.", fg='green')
    except subprocess.CalledProcessError as e:
        secho(f"Error removing secret: {e.stderr.decode().strip()}", fg='red')

# Function to Add Workflow File
def add_workflow(repo, workflow_name, workflow_content, token):
    secho(f"Adding workflow '{workflow_name}' to repo '{repo}'...", fg='green')

    # Clone the repository if not already cloned
    repo_dir = Path(repo.split('/')[-1])
    if not repo_dir.exists():
        clone_command = ["gh", "repo", "clone", repo]
        try:
            subprocess.run(clone_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            secho(f"Cloned repository '{repo}' successfully.", fg='green')
        except subprocess.CalledProcessError as e:
            secho(f"Error cloning repository: {e.stderr.decode().strip()}", fg='red')
            return
    else:
        secho(f"Repository '{repo}' already cloned.", fg='yellow')

    workflow_path = repo_dir / ".github" / "workflows"
    workflow_path.mkdir(parents=True, exist_ok=True)
    workflow_file = workflow_path / workflow_name

    try:
        with open(workflow_file, 'w') as f:
            f.write(workflow_content)
        secho(f"Workflow file '{workflow_name}' created successfully.", fg='green')
    except IOError as e:
        secho(f"Error writing workflow file: {e}", fg='red')
        return

    # Commit and push the workflow file
    try:
        subprocess.run(["git", "add", str(workflow_file)], check=True, cwd=repo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["git", "commit", "-m", f"Add workflow {workflow_name}"], check=True, cwd=repo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["git", "push"], check=True, cwd=repo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        secho(f"Workflow '{workflow_name}' pushed to repository '{repo}' successfully.", fg='green')
    except subprocess.CalledProcessError as e:
        secho(f"Error committing/pushing workflow: {e.stderr.decode().strip()}", fg='red')

# Function to Store Configuration
def store_config(config_key, config_value):
    secho(f"Storing configuration '{config_key}': '{config_value}'...", fg='green')
    config_file = CONFIG_FILE
    config = {}

    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            secho("Error decoding existing config.json. Overwriting.", fg='red')

    config[config_key] = config_value

    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
        secho(f"Configuration '{config_key}' saved successfully.", fg='yellow')
    except IOError as e:
        secho(f"Error saving configuration: {e}", fg='red')

# Function to Save Secret Locally for Persistence
def save_secret_locally(secret_name, secret_value):
    secho(f"Saving secret '{secret_name}' locally...", fg='yellow')
    secrets_file = SECRETS_FILE
    secrets = {}

    if secrets_file.exists():
        try:
            with open(secrets_file, 'r') as f:
                secrets = json.load(f)
        except json.JSONDecodeError:
            secho("Error decoding existing secrets.json. Overwriting.", fg='red')

    secrets[secret_name] = secret_value

    try:
        with open(secrets_file, 'w') as f:
            json.dump(secrets, f, indent=4)
        secho(f"Secret '{secret_name}' saved locally.", fg='yellow')
    except IOError as e:
        secho(f"Error saving secret locally: {e}", fg='red')

# Function to Delete Secret Locally
def delete_secret_locally(secret_name):
    secho(f"Deleting secret '{secret_name}' from local storage...", fg='yellow')
    secrets_file = SECRETS_FILE
    if not secrets_file.exists():
        secho("No secrets found locally.", fg='red')
        return

    try:
        with open(secrets_file, 'r') as f:
            secrets = json.load(f)
    except json.JSONDecodeError:
        secho("Error decoding secrets.json. Cannot delete secret.", fg='red')
        return

    if secret_name in secrets:
        del secrets[secret_name]
        try:
            with open(secrets_file, 'w') as f:
                json.dump(secrets, f, indent=4)
            secho(f"Secret '{secret_name}' deleted from local storage.", fg='yellow')
        except IOError as e:
            secho(f"Error updating secrets.json: {e}", fg='red')
    else:
        secho(f"Secret '{secret_name}' not found in local storage.", fg='red')

# Function to Load Configuration
def load_config():
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config
    except json.JSONDecodeError:
        secho("Error decoding config.json. Please reconfigure your settings.", fg='red')
        return {}

# Function to Initialize Configuration
def initialize_config():
    secho("Welcome to the GitHub Management CLI!", fg='cyan', bold=True)
    secho("Let's set up your GitHub credentials.", fg='blue')
    username = click.prompt("Enter your GitHub username", type=str)
    token = getpass("Enter your GitHub token (input hidden): ")

    store_config('username', username)
    store_config('token', token)
    secho("Configuration saved successfully!", fg='green')

# Function to Ensure Configuration Exists
def ensure_config():
    config = load_config()
    if 'username' not in config or 'token' not in config:
        initialize_config()
        config = load_config()
    return config

# Function to Process Commands Using Strategy Pattern
def process_command(strategy, **kwargs):
    strategy.execute(**kwargs)

# Click Group for CLI
@click.group()
def cli():
    """GitHub Management CLI Tool"""
    pass

# Sub-group for Secrets Management
@cli.group()
def secret():
    """Manage GitHub secrets"""
    pass

# Command to Add a Secret
@secret.command('add')
@click.option('--repo', prompt='Repository name (owner/repo)', help='GitHub repository name in the format owner/repo')
@click.option('--secret_name', prompt='Secret name', help='Name of the secret to add')
@click.option('--secret_value', prompt='Secret value', hide_input=True, confirmation_prompt=True, help='Value of the secret')
def add_secret_command(repo, secret_name, secret_value):
    """Add a new secret to a repository"""
    config = ensure_config()
    strategy = AddSecretStrategy()
    process_command(
        strategy,
        repo=repo,
        secret_name=secret_name,
        secret_value=secret_value,
        token=config.get('token')
    )

# Command to Remove a Secret
@secret.command('remove')
@click.option('--repo', prompt='Repository name (owner/repo)', help='GitHub repository name in the format owner/repo')
@click.option('--secret_name', prompt='Secret name', help='Name of the secret to remove')
def remove_secret_command(repo, secret_name):
    """Remove a secret from a repository"""
    config = ensure_config()
    strategy = RemoveSecretStrategy()
    process_command(
        strategy,
        repo=repo,
        secret_name=secret_name,
        token=config.get('token')
    )

# Sub-group for Workflows Management
@cli.group()
def workflow():
    """Manage GitHub Actions workflows"""
    pass

# Command to Add a Workflow
@workflow.command('add')
@click.option('--repo', prompt='Repository name (owner/repo)', help='GitHub repository name in the format owner/repo')
@click.option('--workflow_name', prompt='Workflow file name (e.g., ci.yml)', help='Name of the workflow file')
@click.option('--workflow_content', prompt='Enter the workflow content (end with EOF on a new line)', type=click.STRING, help='Content of the workflow file')
def add_workflow_command(repo, workflow_name, workflow_content):
    """Add a new GitHub Actions workflow to a repository"""
    config = ensure_config()
    # If the user wants to input multi-line content, handle it
    if 'EOF' in workflow_content:
        secho("Entering multi-line workflow content. Type 'EOF' on a new line to finish.", fg='yellow')
        lines = []
        while True:
            line = click.prompt('', default='', show_default=False)
            if line.strip() == 'EOF':
                break
            lines.append(line)
        workflow_content = '\n'.join(lines)
    strategy = AddWorkflowStrategy()
    process_command(
        strategy,
        repo=repo,
        workflow_name=workflow_name,
        workflow_content=workflow_content,
        token=config.get('token')
    )

# Sub-group for Configurations Management
@cli.group()
def config():
    """Manage configurations"""
    pass

# Command to Store a Configuration
@config.command('store')
@click.option('--config_key', prompt='Configuration key', help='Key for the configuration')
@click.option('--config_value', prompt='Configuration value', help='Value for the configuration')
def store_config_command(config_key, config_value):
    """Store a configuration key-value pair"""
    strategy = StoreConfigStrategy()
    process_command(
        strategy,
        config_key=config_key,
        config_value=config_value
    )

# Command to List Stored Secrets
@secret.command('list')
def list_secrets():
    """List all stored secrets"""
    if not SECRETS_FILE.exists():
        secho("No secrets stored locally.", fg='yellow')
        return
    try:
        with open(SECRETS_FILE, 'r') as f:
            secrets = json.load(f)
        if secrets:
            secho("Stored Secrets:", fg='cyan', bold=True)
            for name, value in secrets.items():
                echo(f"- {name}: {value}")
        else:
            secho("No secrets stored locally.", fg='yellow')
    except json.JSONDecodeError:
        secho("Error decoding secrets.json.", fg='red')

# Command to List Stored Workflows
@workflow.command('list')
def list_workflows():
    """List all stored workflows"""
    if not WORKFLOWS_FILE.exists():
        secho("No workflows stored locally.", fg='yellow')
        return
    try:
        with open(WORKFLOWS_FILE, 'r') as f:
            workflows = json.load(f)
        if workflows:
            secho("Stored Workflows:", fg='cyan', bold=True)
            for name, content in workflows.items():
                echo(f"- {name}:")
                echo(content)
        else:
            secho("No workflows stored locally.", fg='yellow')
    except json.JSONDecodeError:
        secho("Error decoding workflows.json.", fg='red')

# Command to List Configurations
@config.command('list')
def list_configs():
    """List all stored configurations"""
    config = load_config()
    if config:
        secho("Stored Configurations:", fg='cyan', bold=True)
        for key, value in config.items():
            echo(f"- {key}: {value}")
    else:
        secho("No configurations stored.", fg='yellow')

# Command to Initialize Configuration Manually
@config.command('init')
def init_config_command():
    """Initialize or reconfigure GitHub credentials"""
    initialize_config()

# Entry Point
if __name__ == '__main__':
    cli()