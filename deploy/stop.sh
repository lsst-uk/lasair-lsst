if [ $1 ]; then
	ansible-playbook control.yaml --extra-vars "command=stop" --tags=$1
else
	ansible-playbook control.yaml --extra-vars "command=stop"
fi

