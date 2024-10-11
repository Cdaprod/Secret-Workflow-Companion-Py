#!/bin/bash

_pyghm_completions() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts="config secret workflow"

    case "${prev}" in
        config)
            local config_opts="init store list"
            COMPREPLY=( $(compgen -W "${config_opts}" -- "${cur}") )
            return 0
            ;;
        secret)
            local secret_opts="add remove list"
            COMPREPLY=( $(compgen -W "${secret_opts}" -- "${cur}") )
            return 0
            ;;
        workflow)
            local workflow_opts="add list"
            COMPREPLY=( $(compgen -W "${workflow_opts}" -- "${cur}") )
            return 0
            ;;
    esac

    COMPREPLY=( $(compgen -W "${opts}" -- "${cur}") )
    return 0
}

complete -F _pyghm_completions pyghm