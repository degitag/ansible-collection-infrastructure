# Optional interactive Bash SSH agent integration.
if [ -n "${BASH_VERSION:-}" ]; then
# Ansible managed file

# Prüfen, ob die Shell interaktiv ist
if [[ $- == *i* ]]; then
    if [ -z "$SSH_AUTH_SOCK" ]; then
        # Prüfen, ob bereits ein ssh-agent läuft
        if ! pgrep -u "$USER" ssh-agent > /dev/null; then
            eval $(ssh-agent) > /dev/null
        fi
        ssh-add -l > /dev/null || alias ssh='ssh-add -l > /dev/null || ssh-add && unalias ssh; ssh'
    fi
fi
fi
