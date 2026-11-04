#!/bin/bash

show_usage() {
	echo "Usage: $0 <command> <tag_name>"
	echo ""
	echo "Arguments:"
	echo "  <command>   : The action to perform. Valid options: 'start', 'stop', 'status', 'help'."
	echo "  <tag_name>  : Specify a tag to run."
	echo "              : Use 'all' to run without tag filtering."
	echo ""
}

show_tags() {
	# Attempt to retrieve available tags if ansible-playbook is accessible
	echo "Available tags:"
	local tags_output
	# We check if control.yaml exists before trying to list tags to avoid noise
	if [ -f "control.yaml" ]; then
		tags_output=$(ansible-playbook control.yaml --list-tags 2>/dev/null)
		if [ -n "$tags_output" ]; then
			echo "$tags_output" | grep -v "^playbook:" | grep -v "^$" | grep -v "always" \
		       		| sed 's/.*TAGS: //; s/([^)]*)//g' | tr ',' '\n' | tr -d '][[:blank:]' | sort -u | sed 's/^/  - /' 
		else
			echo "  (Unable to retrieve tags. Ensure control.yaml is valid.)"
		fi
	else
		echo "  (control.yaml not found in current directory.)"
	fi
}

COMMAND_ARG="$1"
TAG_ARG="$2"

# Check if no arguments are provided
if [ -z "$COMMAND_ARG" ]; then
	show_usage
	exit 1
fi

# Show help if requested
if [ "$COMMAND_ARG" = "help" ]; then
	show_usage
        show_tags
	exit 1
fi

# Validate the command argument
if [ "$COMMAND_ARG" != "start" ] && [ "$COMMAND_ARG" != "stop" ] && [ "$COMMAND_ARG" != "status" ]; then
	echo "Error: Invalid command '$COMMAND_ARG'. Must be 'start', 'stop' or 'status'."
	show_usage
	exit 1
fi

# Construct the extra-vars string
EXTRA_VARS="command=$COMMAND_ARG"

# Handle the second argument (Tag)
if [ -z "$TAG_ARG" ] && [ "$COMMAND_ARG" != "status" ]; then
	# If no tag is provided, show usage (which now includes tag list)
	show_usage
	exit 1
fi

if [ "$TAG_ARG" = "all" ]; then
	# Run without --tags flag
	ansible-playbook control.yaml --extra-vars "$EXTRA_VARS"
else
	# Run with the specified tag
	ansible-playbook control.yaml --extra-vars "$EXTRA_VARS" --tags="$TAG_ARG"
fi

