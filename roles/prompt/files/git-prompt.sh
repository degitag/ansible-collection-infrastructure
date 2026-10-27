# Sourced from an interactive Bash profile. No prompt side effects here.
parse_git_branch() {
    local branch status
    branch=$(git symbolic-ref --short HEAD 2>/dev/null || git describe --tags --exact-match 2>/dev/null) || return 0
    status=$(git status --porcelain 2>/dev/null)
    if [ -n "$status" ]; then
        printf ' (%s*)' "$branch"
    else
        printf ' (%s)' "$branch"
    fi
}
