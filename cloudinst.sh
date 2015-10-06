#!/usr/bin/ksh
# File Desciption : IBM script to install/remove/query cloudinit and
#                   its requisites
# Script Version : 1.2
# Date :   10/05/2015
# Author : Scott Tran
# Description :  This script performs 3 main operations.  They are:
#      - Query the size of the cloudinit package and its requisites
#      - Install the cloudinit package and its requisites
#      - Remove the cloudinit package and its requisites
#      Note:  Some packages after installation will experience
#             difficulties when they are uninstalled.  The reason is
#             because of the rpm dependencies created with the RPM
#             packages and the rpm command.  The RPM package can be
#             removed but only with a force (--nodeps) flag, which
#             this script will not do.  With the --nodeps removal
#             of the RPM, the rpm command will experience problem
#             and will not execute correctly.  The only solution
#             after running a --nodeps removal that breaks the rpm
#             command is to do a force re-install of the rpm.rte fileset.
#
# Version History:
#      1.0    Initial version
#      1.1    Change fdupes location at line 60
#      1.2    Change rpm flag to "-Uvh" from "-ivh" for install
######################################################################

######################################################################
#
# Global declaration
#
######################################################################

COMMAND="$0"
AWK="/usr/bin/awk"
BASENAME="/usr/bin/basename"
EXPR="/usr/bin/expr"
GREP="/usr/bin/grep"
RPM="/usr/bin/rpm"
TR="/usr/bin/tr"
WC="/usr/bin/wc"

set -A rpmName \
        http://www.bullfreeware.com/download/bin/1439/bzip2-1.0.6-2.aix6.1.ppc.rpm \
        http://www.bullfreeware.com/download/bin/1441/db-4.8.24-4.aix6.1.ppc.rpm \
        http://www.bullfreeware.com/download/bin/1639/expat-2.1.0-1.aix6.1.ppc.rpm \
        http://www.bullfreeware.com/download/bin/2046/gmp-5.1.3-1.aix6.1.ppc.rpm \
        http://www.bullfreeware.com/download/bin/1587/libffi-3.0.11-1.aix6.1.ppc.rpm \
        http://www.bullfreeware.com/download/bin/2076/openssl-1.0.1g-1.aix6.1.ppc.rpm \
        http://www.bullfreeware.com/download/bin/1908/zlib-1.2.5-6.aix6.1.ppc.rpm \
        http://www.bullfreeware.com/download/bin/2013/gettext-0.17-8.aix6.1.ppc.rpm \
        http://www.bullfreeware.com/download/bin/1446/gdbm-1.10-1.aix6.1.ppc.rpm \
        http://www.bullfreeware.com/download/bin/2024/libiconv-1.14-1.aix6.1.ppc.rpm \
        http://www.bullfreeware.com/download/bin/2091/bash-4.2-9.aix6.1.ppc.rpm \
        http://www.bullfreeware.com/download/bin/1918/info-5.0-2.aix6.1.ppc.rpm \
        http://www.bullfreeware.com/download/bin/1464/readline-6.2-3.aix6.1.ppc.rpm \
        http://www.bullfreeware.com/download/bin/1486/ncurses-5.9-3.aix6.1.ppc.rpm \
        http://www.bullfreeware.com/download/bin/1742/sqlite-3.7.15.2-2.aix6.1.ppc.rpm \
        http://www.bullfreeware.com/download/bin/2064/python-2.7.6-1.aix6.1.ppc.rpm \
        http://www.bullfreeware.com/download/bin/2332/fdupes-1.51-1.aix6.1.ppc.rpm \
        http://www.bullfreeware.com/download/bin/2065/python-devel-2.7.6-1.aix6.1.ppc.rpm \
        http://www.bullfreeware.com/download/bin/2117/python-xml-0.8.4-1.aix6.1.ppc.rpm \
        http://www.bullfreeware.com/download/bin/2101/python-boto-2.34.0-1.aix6.1.noarch.rpm \
        http://www.bullfreeware.com/download/bin/2099/python-argparse-1.2.1-1.aix6.1.noarch.rpm \
        http://www.bullfreeware.com/download/bin/2102/python-cheetah-2.4.4-2.aix6.1.ppc.rpm \
        http://www.bullfreeware.com/download/bin/2103/python-configobj-5.0.5-1.aix6.1.noarch.rpm \
        http://www.bullfreeware.com/download/bin/2106/python-jsonpointer-1.0.c1ec3df-1.aix6.1.noarch.rpm \
        http://www.bullfreeware.com/download/bin/2105/python-jsonpatch-1.8-1.aix6.1.noarch.rpm \
        http://www.bullfreeware.com/download/bin/2108/python-oauth-1.0.1-1.aix6.1.noarch.rpm \
        http://www.bullfreeware.com/download/bin/2112/python-pyserial-2.7-1.aix6.1.ppc.rpm \
        http://www.bullfreeware.com/download/bin/1858/python-prettytable-0.7.2-1.aix6.1.noarch.rpm \
        http://www.bullfreeware.com/download/bin/2114/python-requests-2.4.3-1.aix6.1.noarch.rpm \
        http://www.bullfreeware.com/download/bin/1632/libyaml-0.1.4-1.aix6.1.ppc.rpm \
        http://www.bullfreeware.com/download/bin/2192/python-PyYAML-3.11-2.aix6.1.ppc.rpm \
        http://www.bullfreeware.com/download/bin/1903/python-six-1.3.0-1.aix6.1.noarch.rpm \
        http://www.bullfreeware.com/download/bin/2115/python-setuptools-0.9.8-2.aix6.1.noarch.rpm \
        ftp://ftp.software.ibm.com/aix/freeSoftware/aixtoolbox/RPMS/ppc/cloudinit/cloud-init-0.7.5-4.1.aix6.1.ppc.rpm

######################################################################
#
# Function declaration
#
######################################################################

#################################################################
# List the RPMs and get their package size.
# If the package is installed on the machine,
# then don't get the size.
#################################################################
function query_rpm {

        typeset -i totsize=0
        typeset -i size=0
        typeset -i count=0
        typeset -i cfield=4
        typeset -i sfield=15
        typeset -i zfield=10
        typeset -i length=`get_length`
        typeset line=`printf "%$(( ${cfield} + ${length} + ${sfield} + ${zfield} ))s\n" | $TR " " "="`

        echo "Querying RPM packages and requisites for Cloudinit."
        echo "This may take some time depending on network speed.\n"

        printf "%${cfield}s%${length}s%${sfield}s%${zfield}s\n" "No." "RPM Package" "Status" "Size"
        print "$line"
        for index in ${rpmName[@]}; do
                count=$count+1
                base_value=`$BASENAME $index`
                rpm_name=`echo ${base_value%%.aix*}`

                if [[ $( is_installed $rpm_name; echo $?) -eq 1 ]]; then
                        printf "%${cfield}s%${length}s%${sfield}s%${zfield}s\n" "$count" "$base_value" "Installed" "---"
                else
                        size=`$RPM -qip $index | $GREP '^Size[:blank:]*:*' | $AWK '{print $3}'`
                        isnum $size
                        if [[ $? -eq 0 ]]; then
                                site=`echo ${index%%/download*}`
                                echo "Unable to query the RPM packages."
                                echo "Please check to see if the firewall is blocking access to:"
                                echo "$site"
                                exit 1
                        fi
                        printf "%${cfield}s%${length}s%${sfield}s%${zfield}s\n" "$count" "$base_value" "---" "$size"
                        totsize=$totsize+$size
                fi
        done
        print "$line"
        printf "%-$(( ${cfield} + ${length} + ${sfield} ))s%${zfield}s\n\n" "Total Size" "$totsize"

        totsize=$(( ($totsize/1024)/1024 ))
        printf "%-$(( ${cfield} + ${length} + ${sfield} ))s%${zfield}s\n" "Cloudinit and Requisites Size in MB Needed:" "${totsize}M"
      
        exit 0
}

#################################################################
# Install the RPM packages from the rpmName array
#################################################################
function install_rpm {

        typeset -i count=0

        echo "Searching RPM packages to install ..."
        echo "This may take some time depending on network speed."

        for index in ${rpmName[@]}; do
                base_value=`$BASENAME $index`
                rpm_name=`echo ${base_value%%.aix*}`

                if [[ $( is_installed $rpm_name; echo $?) -eq 0 ]]; then      

                        # Special flag for gettext
                        if [[ $rpm_name = gettext* ]]; then
                                $RPM -Uvh --nodeps $index
                        else
                                $RPM -Uvh $index
                        fi

                        if [[ $? -ne 0 ]]; then
                                echo "Error: Unable to install RPM packages."
                                echo "Please check the filesystem size and expand /opt if needed."

                                if [[ $count -eq 0 ]]; then
                                        site=`echo ${index%%/download*}`
                                        echo "Please check to see if the firewall is blocking access to:"
                                        echo "$site"
                                        exit 1
                                fi
                                echo "Rerun the install operation to continue with installation"
                                exit 2
                        fi
                        count=count+1
                fi
        done

        if [[ $count -eq 0 ]]; then
                echo "No install needed.  All packages are already installed."
        fi

        exit 0
}

#################################################################
# Uninstall the RPM in the array list from the machine
#################################################################
function remove_rpm {

        typeset -i count=${#rpmName[*]}-1
        typeset -i index=0
        set -A new_array

        echo "Searching for RPM packages to uninstall ...\n"

        while [[ $count -ge 0 ]]; do
                base_value=`$BASENAME ${rpmName[$count]}`
                rpm_name=`echo ${base_value%%.aix*}`
                if [[ $( is_installed $rpm_name; echo $?) -eq 1 ]]; then
                        echo "Uninstalling $rpm_name"
                        $RPM -e $rpm_name
                        if [[ $? -ne 0 ]]; then
                                new_array[$index]=$rpm_name
                                index=$index+1
                        fi
                fi
                (( count=count-1 ))
        done

        echo "\nThe following RPM packages could not be uninstalled due to dependencies."
        echo "You can try a force removal by using the rpm -e \"--nodeps\" flag."
        echo "Note: A force removal may cause the rpm command to not run properly."
        echo "If the force removal is used, a force reinstall of the rpm.rte "
        echo "fileset is needed to get the rpm command to work."

        for i in ${new_array[@]}; do
                echo "$i"
        done

        exit 0
}

#################################################################
# Print the Usage
#################################################################
function print_usage {
        typeset exit_code=$1

        echo "usage: $COMMAND [ -o { query | install | remove } | -h ]"
        echo "\t-o query\tquery the size of the cloudinit RPM package and its requisites"
        echo "\t-o install\tinstall the cloudinit RPM package and its requisites"
        echo "\t-o remove\tremove the cloudinit RPM package and its requisites"
        echo "\t-h\t\tprint usage"

        exit $exit_code
}

#################################################################
# Get the longest string length of the RPM package in the array
#################################################################
function get_length {

        typeset -i length=0
        typeset -i maxlength=0

        for index in ${rpmName[@]}; do
                base_value=`$BASENAME $index`
                length=`echo $base_value | $WC -c`
                if [[ $length > $maxlength ]]; then
                        maxlength=$length
                fi
        done

        echo "$maxlength"
}

#################################################################
# Check if RPM is installed on machine
#################################################################
function is_installed {

        typeset rpm_name=$1
        typeset -i rc=0

        $RPM -q $rpm_name >/dev/null 2>&1 && rc=1

        return $rc
}

#################################################################
# Check to see if a value is an integer
#################################################################
function isnum {

        typeset size=$1
        typeset -i rc=0

        $EXPR $size + 0 >/dev/null 2>&1 && rc=1

        return $rc
}

######################################################################
#
# MAIN Main main
#
######################################################################

while getopts ho: c 2>/dev/null; do
        case ${c} in
        o)      # operation
                operation=${OPTARG}
                ;;
        h)      # help
                print_usage 0
                ;;
        \?)     # unknown option
                print_usage 1
                ;;
        esac
done

shift $((OPTIND - 1))
ARGUMENT=$*

if [[ -n $ARGUMENT ]]; then
        echo "Error: Argument without flag"
        print_usage 2
fi

if [[ -z $operation ]]; then
        operation="query"
fi

case $operation in
        "install" ) install_rpm;;
        "remove" ) remove_rpm;;
        "query" ) query_rpm;;
        *) echo "Error: Invalid operation"; print_usage 3;;
esac
