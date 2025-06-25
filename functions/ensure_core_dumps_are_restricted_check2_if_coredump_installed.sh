#!/usr/bin/env bash
{
# Checking the if systemd-coredump is installed
coredump_is_install=$(systemctl list-unit-files | grep coredump)
#storage=$(grep -Psi -- '^\s*Storage\s*=\s*none\s*$' /etc/systemd/coredump.conf)
#processSize=$(grep -Psi -- '^\s*ProcessSizeMax\s*=\s*0' /etc/systemd/coredump.conf)
storage=$(grep -Psi -- \'^\s*Storage\s*=\s*none\s*$\' ~/Documents/grep.txt)
processSize=$(grep -Psi -- \'^\s*ProcessSizeMax\s*=\s*0\' ~/Documents/grep.txt)
overall_pass=False


if[-n '$coredump_is_install'; then
	if [-z '$storage'];then
		#echo "** FAIL **- Storage is not set to none"
		overall_pass = False
	elif [-z '$processSize'];then
		#echo "** FAIL **- Storage is not set to none"
		overall_pass = False
	else
		overall_pass = True
	fi
else
	overall_pass = True
fi

if overall_pass;then
	echo "** PASS **"
	exit 0
else
	echo "** FAIL **"
	exit 1
fi

}