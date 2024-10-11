# GitComp (Secret Workflow Companion)

A Python-based command-line interface tool designed to simplify the management of GitHub secrets and workflows, featuring interactive prompts and persistent storage.

## Features

1. Interactive CLI Interface: Utilize the click library to create a more intuitive and interactive command-line interface.
2. Persistent Storage: Store user authentication details and added secrets/workflows in local JSON files (config.json, secrets.json, and workflows.json) to retain information between uses.
3. Secure Storage Considerations: While this example uses plain JSON files for simplicity, consider using encryption or secure storage solutions (like keyring) for sensitive data in production environments.
4. Enhanced User Experience: Add commands for listing and removing secrets/workflows, and provide colored outputs for better readability.
5. Bash Alias and Autocomplete: Easy-to-use bash alias with command autocomplete functionality.

## Installation

### Prerequisites

- Python 3.6 or later
- GitHub CLI (gh)
- make (usually pre-installed on most Unix-like systems)

### Steps

1. Clone the repository:
   ```
   git clone https://github.com/Cdaprod/secret-workflow-companion.git
   cd secret-workflow-companion
   ```

2. Install the tool:
   ```
   sudo make install
   ```

3. Restart your terminal or run:
   ```
   source ~/.bash_profile
   ```

4. Install and authenticate GitHub CLI:
   Follow the [GitHub CLI Installation Guide](https://cli.github.com/manual/installation).

5. Verify GitHub CLI authentication:
   ```
   gh auth status
   ```

## Usage

After installation, you can use the `gitcomp` command followed by subcommands. The tool supports command autocomplete.

### Initial Configuration

```
gitcomp config init
```

### Adding a Secret

```
gitcomp secret add
```

### Removing a Secret

```
gitcomp secret remove
```

### Listing Stored Secrets

```
gitcomp secret list
```

### Adding a GitHub Actions Workflow

```
gitcomp workflow add
```

### Listing Stored Workflows

```
gitcomp workflow list
```

### Storing a Configuration Key-Value Pair

```
gitcomp config store
```

### Listing Stored Configurations

```
gitcomp config list
```

## Uninstallation

To uninstall the tool, run:

```
sudo make uninstall
```

Then restart your terminal or run:

```
source ~/.bash_profile
```

## Security Considerations

- The script stores GitHub tokens and secrets in plain JSON files. This is not secure for production environments.
- Recommendations:
  - Use environment variables to store sensitive information.
  - Implement encryption for local storage.
  - Utilize secure storage solutions like keyring for managing credentials.
- Ensure that config.json, secrets.json, and workflows.json are added to your .gitignore file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.