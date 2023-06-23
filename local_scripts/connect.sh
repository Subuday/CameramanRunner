#!/bin/bash

# Specify the command to be executed in the new terminal window
command_to_execute="ssh -i $1 ubuntu@$2"

# Launch the terminal and execute the command
osascript -e "tell application \"Terminal\" to do script \"$command_to_execute\""
