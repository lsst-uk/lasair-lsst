if [ $1 ]; then
	ansible-playbook control.yaml --extra-vars "command=start" --tags=$1
else
	ansible-playbook control.yaml --extra-vars "command=start" --tags=$1
fi

