# Makefile for GitComp

# Python interpreter
PYTHON := python3

# Project name
PROJECT_NAME := gitcomp

# Main script
MAIN_SCRIPT := main.py

# Bash profile file
BASH_PROFILE := ~/.bash_profile

# Autocomplete script
AUTOCOMPLETE_SCRIPT := scripts/autocompletion.sh

# Installation directory
INSTALL_DIR := /usr/local/bin

.PHONY: all install uninstall clean

all: install

install: $(MAIN_SCRIPT) $(AUTOCOMPLETE_SCRIPT)
	@echo "Installing $(PROJECT_NAME)..."
	@mkdir -p $(INSTALL_DIR)
	@cp $(MAIN_SCRIPT) $(INSTALL_DIR)/$(PROJECT_NAME)
	@chmod +x $(INSTALL_DIR)/$(PROJECT_NAME)
	@echo "Creating bash alias and enabling autocomplete..."
	@echo "" >> $(BASH_PROFILE)
	@echo "# $(PROJECT_NAME) alias and autocomplete" >> $(BASH_PROFILE)
	@echo "alias $(PROJECT_NAME)='$(INSTALL_DIR)/$(PROJECT_NAME)'" >> $(BASH_PROFILE)
	@echo "source $(PWD)/$(AUTOCOMPLETE_SCRIPT)" >> $(BASH_PROFILE)
	@echo "Installation complete. Please restart your terminal or run 'source $(BASH_PROFILE)' to use the alias."

uninstall:
	@echo "Uninstalling $(PROJECT_NAME)..."
	@rm -f $(INSTALL_DIR)/$(PROJECT_NAME)
	@sed -i.bak '/# $(PROJECT_NAME) alias and autocomplete/,+2d' $(BASH_PROFILE)
	@echo "Uninstallation complete. Please restart your terminal or run 'source $(BASH_PROFILE)' to apply changes."

clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete