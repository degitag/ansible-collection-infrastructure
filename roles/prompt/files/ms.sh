#!/bin/bash
# Ansible managed file
pane="$(tmux new-window -P -n "${*}" "ssh $1")"
pane1="$pane"
win="${pane/.*}"
tmux select-window -t "$win"
shift
c=1
while [ $# -gt 0 ]; do
    (( c++ ))
    pane=$(tmux split-window -P -t "$pane" -d "ssh $1")
    tmux select-layout -t "$win" tiled
    #tmux select-pane -t "$pane"
    shift
done
tmux set-window-option -t "$win" synchronize-panes
tmux select-layout -t "$win" tiled
tmux select-pane -t "$pane1"