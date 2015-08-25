cloud-init-0.7.5
===================
# AIX cloud-init support #
-------------

#### Instruction for building the AIX RPM package for cloud-init ####

1.  Download the cloud-init ZIP file and transfer the ZIP file to an AIX machine.
    The instruction below will use /tmp/CLOUD-INIT as the workspace for building the AIX cloud-init RPM package.
    
    - mkdir /tmp/CLOUD-INIT
    - cp cloud-init-0.7.5-master.zip /tmp/CLOUD-INIT
    - cd /tmp/CLOUD-INIT
    
2.  Extract the cloud-init ZIP file
    - jar -xvf cloud-init-0.7.5-master.zip
    
3.  Rename the folder from cloud-init-0.7.5-master to cloud-init-0.7.5
    - mv cloud-init-0.7.5 cloud-init-0.7.5
    
4.  Add executable permission to executable files
    - chmod -Rf +x /tmp/CLOUD-INIT/cloud-init-0.7.5/tools
    - chmod -Rf +x /tmp/CLOUD-INIT/cloud-init-0.7.5/bin
    
5.  Copy the spec file from cloud-init to the RPM build packages path
    - cp /tmp/CLOUD-INIT/cloud-init-0.7.5/packages/aix/cloud-init.spec.in /opt/freeware/src/packages/SPECS/cloud-init.spec
    
6.  tar and gzip the cloudinit file so that RPM can build it
    - tar -cvf cloud-init-0.7.5.tar cloud-init-0.7.5
    - gzip cloud-init-0.7.5.tar
    
7.  Copy the cloudinit gzip file to the RPM directory to be built
    - cp cloud-init-0.7.5.tar.gz /opt/freeware/src/packages/SOURCES/cloud-init-0.7.5.tar.gz
    
8.  Build the cloudinit RPM
    - rpm -v -bb /opt/freeware/src/packages/SPECS/cloud-init.spec
    
9.  Install the cloud-init RPM package.
    - rpm -ivh /opt/freeware/src/packages/RPMS/ppc/cloud-init-0.7.5-4.1.aix6.1.ppc.rpm



#### AIX Cloudinit RPM Package Requisite ####

>The following RPM packages are needed to install python and cloud-init on AIX.
The RPM packages can be obtained from the following website:
[http://www.bullfreeware.com/][1]

>The following packages are listed in the order it was installed.

> Packages needed for installing python on AIX

> *Note:*

>- the RPM flag of *--nodeps* is needed for installing gettext-0.17-8.aix6.1.ppc.rpm

- [bzip2-1.0.6-2.aix6.1.ppc.rpm][2]
- [db-4.8.24-4.aix6.1.ppc.rpm][3]
- [expat-2.1.0-1.aix6.1.ppc.rpm][4]
- [gmp-5.1.3-1.aix6.1.ppc.rpm][5]
- [libffi-3.0.11-1.aix6.1.ppc.rpm][6]
- [openssl-1.0.1g-1.aix6.1.ppc.rpm][7]
- [zlib-1.2.5-6.aix6.1.ppc.rpm][8]
- [gettext-0.17-8.aix6.1.ppc.rpm][9]
- [gdbm-1.10-1.aix6.1.ppc.rpm][10]
- [libiconv-1.14-1.aix6.1.ppc.rpm][11]
- [bash-4.2-9.aix6.1.ppc.rpm][12]
- [info-5.0-2.aix6.1.ppc.rpm][13]
- [readline-6.2-3.aix6.1.ppc.rpm][14]
- [ncurses-5.9-3.aix6.1.ppc.rpm][15]
- [sqlite-3.7.15.2-2.aix6.1.ppc.rpm][16]
- [python-2.7.6-1.aix6.1.ppc.rpm][17]
- [fdupes-1.51-1.aix6.1.ppc.rpm][18]

#### Packages needed for installing cloud-init on AIX ####

- [python-devel-2.7.6-1.aix6.1.ppc.rpm][19]
- [python-xml-0.8.4-1.aix6.1.ppc.rpm][20]
- [python-boto-2.34.0-1.aix6.1.noarch.rpm][21]
- [python-argparse-1.2.1-1.aix6.1.noarch.rpm][22]
- [python-cheetah-2.4.4-2.aix6.1.ppc.rpm][23]
- [python-configobj-5.0.5-1.aix6.1.noarch.rpm][24]
- [python-jsonpointer-1.0.c1ec3df-1.aix6.1.noarch.rpm][25]
- [python-jsonpatch-1.8-1.aix6.1.noarch.rpm][26]
- [python-oath-1.0.1-1.aix6.1.noarch.rpm][27]
- [python-pyserial-2.7-1.aix6.1.ppc.rpm][28]
- [python-prettytable-0.7.2-1.aix6.1.noarch.rpm][29]
- [python-requests-2.4.3-1.aix6.1.noarch.rpm][30]
- [libyaml-0.1.4-1.aix6.1.ppc.rpm][31]
- [python-PyYAML-3.11-2.aix6.1.ppc.rpm][32]
- [python-six-1.3.0-1.aix6.1.noarch.rpm][33]
- [python-setuptools-0.9.8-2.aix6.1.noarch.rpm][34]

[1]:http://www.bullfreeware.com/
[2]:http://www.bullfreeware.com/download/bin/1439/bzip2-1.0.6-2.aix6.1.ppc.rpm
[3]:http://www.bullfreeware.com/download/bin/1441/db-4.8.24-4.aix6.1.ppc.rpm
[4]:http://www.bullfreeware.com/download/bin/1639/expat-2.1.0-1.aix6.1.ppc.rpm
[5]:http://www.bullfreeware.com/download/bin/2046/gmp-5.1.3-1.aix6.1.ppc.rpm
[6]:http://www.bullfreeware.com/download/bin/1587/libffi-3.0.11-1.aix6.1.ppc.rpm
[7]:http://www.bullfreeware.com/download/bin/2076/openssl-1.0.1g-1.aix6.1.ppc.rpm
[8]:http://www.bullfreeware.com/download/bin/1908/zlib-1.2.5-6.aix6.1.ppc.rpm
[9]:http://www.bullfreeware.com/download/bin/2013/gettext-0.17-8.aix6.1.ppc.rpm
[10]:http://www.bullfreeware.com/download/bin/1446/gdbm-1.10-1.aix6.1.ppc.rpm
[11]:http://www.bullfreeware.com/download/bin/2024/libiconv-1.14-1.aix6.1.ppc.rpm
[12]:http://www.bullfreeware.com/download/bin/2091/bash-4.2-9.aix6.1.ppc.rpm
[13]:http://www.bullfreeware.com/download/bin/1918/info-5.0-2.aix6.1.ppc.rpm
[14]:http://www.bullfreeware.com/download/bin/1464/readline-6.2-3.aix6.1.ppc.rpm
[15]:http://www.bullfreeware.com/download/bin/1486/ncurses-5.9-3.aix6.1.ppc.rpm
[16]:http://www.bullfreeware.com/download/bin/1742/sqlite-3.7.15.2-2.aix6.1.ppc.rpm
[17]:http://www.bullfreeware.com/download/bin/2064/python-2.7.6-1.aix6.1.ppc.rpm
[18]:http://www.bullfreeware.com/download/bin/2332/fdupes-1.51-1.aix6.1.ppc.rpm
[19]:http://www.bullfreeware.com/download/bin/2065/python-devel-2.7.6-1.aix6.1.ppc.rpm
[20]:http://www.bullfreeware.com/download/bin/2117/python-xml-0.8.4-1.aix6.1.ppc.rpm
[21]:http://www.bullfreeware.com/download/bin/2101/python-boto-2.34.0-1.aix6.1.noarch.rpm
[22]:http://www.bullfreeware.com/download/bin/2099/python-argparse-1.2.1-1.aix6.1.noarch.rpm
[23]:http://www.bullfreeware.com/download/bin/2102/python-cheetah-2.4.4-2.aix6.1.ppc.rpm
[24]:http://www.bullfreeware.com/download/bin/2103/python-configobj-5.0.5-1.aix6.1.noarch.rpm
[25]:http://www.bullfreeware.com/download/bin/2106/python-jsonpointer-1.0.c1ec3df-1.aix6.1.noarch.rpm
[26]:http://www.bullfreeware.com/download/bin/2105/python-jsonpatch-1.8-1.aix6.1.noarch.rpm
[27]:http://www.bullfreeware.com/download/bin/2108/python-oauth-1.0.1-1.aix6.1.noarch.rpm
[28]:http://www.bullfreeware.com/download/bin/2112/python-pyserial-2.7-1.aix6.1.ppc.rpm
[29]:http://www.bullfreeware.com/download/bin/1858/python-prettytable-0.7.2-1.aix6.1.noarch.rpm
[30]:http://www.bullfreeware.com/download/bin/2114/python-requests-2.4.3-1.aix6.1.noarch.rpm
[31]:http://www.bullfreeware.com/download/bin/1632/libyaml-0.1.4-1.aix6.1.ppc.rpm
[32]:http://www.bullfreeware.com/download/bin/2192/python-PyYAML-3.11-2.aix6.1.ppc.rpm
[33]:http://www.bullfreeware.com/download/bin/1903/python-six-1.3.0-1.aix6.1.noarch.rpm
[34]:http://www.bullfreeware.com/download/bin/2115/python-setuptools-0.9.8-2.aix6.1.noarch.rpm

#### AIX Cloudinit cloudinst.sh script ####
>The cloudinst.sh script is provided to facilitate the installation of Cloudinit and its requisites on AIX.  When executed without argument, the query operation will run to determine the package size needed for the installation.  This size can then be used to expand the /opt filesystem on the system to accomodate the installation of cloud-init and its requisites.  Please make sure that machine installing cloud-init must be firewall authenticated to download the RPM packages from http://www.bullfreeware.com.

    # usage: cloudinst.sh [ -o { query | install | remove } | -h ]
        -o query        query the size of the cloudinit RPM package and its requisites
        -o install      install the cloudinit RPM package and its requisites
        -o remove       remove the cloudinit RPM package and its requisites
        -h              print usage
