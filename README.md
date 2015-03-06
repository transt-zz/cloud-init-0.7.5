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
    - cp /tmp/CLOUD-INIT/cloud-init-0.7.5/packages/aix/cloud-init.spec /opt/freeware/src/packages/SPECS/cloud-init.spec
    
6.  tar and gzip the cloudinit file so that RPM can build it
    - tar -cvf cloud-init-0.7.5.tar cloud-init-0.7.5
    - gzip cloud-init-0.7.5.tar
    
7.  Copy the cloudinit gzip file to the RPM directory to be built
    - cp cloud-init-0.7.5.tar.gz /opt/freeware/src/packages/SOURCES/cloud-init-0.7.5.tar.gz
    
8.  Build the cloudinit RPM
    - rpm -v -bb /opt/freeware/src/packages/SPEC/cloud-init.spec
    
9.  Install the cloud-init RPM package.
    - rpm -ivh /opt/freeware/src/packages/RPMS/ppc/cloud-init-0.7.5-4.1.aix6.1.ppc.rpm



#### AIX Cloudinit RPM Package Requisite ####

>The following RPM packages are needed to install python and cloud-init on AIX.
The RPM packages can be obtained from the following website:
[http://www.bullfreeware.com/][1]

>The following packages are listed in the order it was installed.

> Packages needed for installing python on AIX

> *Note:*

>- the RPM flag of *--nodep* is needed for installing gettext-0.17-8.aix6.1.ppc.rpm

- bzip2-1.0.6-2.aix6.1.ppc.rpm
- db-4.8.24-4.aix6.1.ppc.rpm
- expat-2.1.0-1.aix6.1.ppc.rpm
- gmp-5.1.3-1.aix6.1.ppc.rpm
- libffi-3.0.11-1.aix6.1.ppc.rpm
- openssl-1.0.1g-1.aix6.1.ppc.rpm
- zlib-1.2.5-6.aix6.1.ppc.rpm
- gettext-0.17-8.aix6.1.ppc.rpm
- gdbm-1.10-1.aix6.1.ppc.rpm
- libiconv-1.14-1.aix6.1.ppc.rpm
- bash-4.2-9.aix6.1.ppc.rpm
- info-5.0-2.aix6.1.ppc.rpm
- readline-6.2-3.aix6.1.ppc.rpm
- ncurses-5.9-3.aix6.1.ppc.rpm
- sqlite-3.7.15.2-2.aix6.1.ppc.rpm
- python-2.7.6-1.aix6.1.ppc.rpm

#### Packages needed for installing cloud-init on AIX ####

- python-devel-2.7.6-1.aix6.1.ppc.rpm
- python-xml-0.8.4-1.aix6.1.ppc.rpm
- python-boto-2.34.0-1.aix6.1.noarch.rpm
- python-argparse-1.2.1-1.aix6.1.noarch.rpm
- python-cheetah-2.4.4-2.aix6.1.ppc.rpm
- python-configobj-5.0.5-1.aix6.1.noarch.rpm
- python-jsonpointer-1.0.c1ec3df-1.aix6.1.noarch.rpm
- python-jsonpatch-1.8-1.aix6.1.noarch.rpm
- python-oath-1.0.1-1.aix6.1.noarch.rpm
- python-pyserial-2.7-1.aix6.1.ppc.rpm
- python-prettytable-0.7.2-1.aix6.1.noarch.rpm
- python-requests-2.4.3-1.aix6.1.noarch.rpm
- libyaml-0.1.4-1.aix6.1.ppc.rpm
- python-PyYAML-3.11-2.aix6.1.ppc.rpm
- python-six-1.3.0-1.aix6.1.noarch.rpm

[1]:http://www.bullfreeware.com/
