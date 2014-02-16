Password Locker
====================
Password Locker is an open source cross-platform program built with 
wxPython. It is for storing your website passwords and other information in a
securely encrypted file. It can be used in conjunction with a cloud service
such as Dropbox or SkyDrive to securely back up your password lists.

It is tested in Windows 8 and Ubuntu, but should work in any 
platform that wxPython works in.

Installation
--------------------------------------------

### Ubuntu/Linux

Make sure python 2.7.x is installed (type <code>python --version</code> 
at the terminal) then install wxPython with

    sudo apt-get install python-wxgtk2.8

Clone this repo to a folder on your computer with

    git clone git://github.com/tgvoskuilen/PasswordLocker.git
    
Run the <code>run.py</code> script to open the program.

### Windows 8

First install python 2.7 for [Windows](http://www.python.org/getit/), 
then install wxPython 2.8 with the appropriate
[Windows binary](http://www.wxpython.org/download.php). Finally, install
pyCrypto 2.6 with the appropriate 
[Windows binary](http://www.voidspace.org.uk/python/modules.shtml#pycrypto) or
similar.

Then download the source files for 
[pyBrew](http://www.github.com/tgvoskuilen/PasswordLocker/archive/master.zip) and
unzip them to a folder anywhere on your computer. Double click on 
<code>run.py</code> to start the program.

### Mac OSX and Others

Follow the instructions for Windows 7, but choose the Mac installers instead.
I have not tested this.


