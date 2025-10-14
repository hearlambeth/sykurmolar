#! /usr/bin/bash
echo "Creating audio performance environment..."

start_cpupower_service="systemctl start cpupower.service"
vm_swappiness="sysctl vm.swappiness=10"
max_user_watches="sysctl fs.inotify.max_user_watches=600000"

if $start_cpupower_service; then
	echo "SUCCESS: cpupower.service"
else
	echo "FAILED: cpupower.service"
	exit 1
fi

if $vm_swappiness; then
	echo "SUCCESS: vm.swappiness"
else
	echo "FAILED: vm.swappiness"
	exit 1
fi

if $max_user_watches; then
	echo "SUCCESS: max_user_watches"
else
	echo "FAILED: max_user_watches"
	exit 1
fi

echo "...audio performance environment created"

exit 0