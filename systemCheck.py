import os
from os.path import dirname
from os.path import exists
from os.path import join
import subprocess
import sys

def main():
    print "#####   System Information   #####"
    print ""
    print "Platform:", sys.platform
    print "Operating System:", os.name
    print "Python:", sys.version.replace("\n", "")
    print os.uname()
    print ""

    try:
        import pycurl
        print "pycurl:", pycurl.version
    except:
        print "pycurl:", "missing"

    try:
        import Crypto
        print "py-crypto:", Crypto.__version__
    except:
        print "py-crypto:", "missing"


    try:
        import OpenSSL
        print "OpenSSL:", OpenSSL.version.__version__
    except:
        print "OpenSSL:", "missing"

    try:
        import Image
        print "image libary:", Image.VERSION
    except:
        print "image libary:", "missing"

    try:
        import django
        print "django:", django.get_version()
    except:
        print "django:", "missing"

    try:
        import PyQt4.QtCore
        print "pyqt:", PyQt4.QtCore.PYQT_VERSION_STR
    except:
        print "pyqt:", "missing"

    print ""
    print ""
    print "#####   System Status   #####"
    print ""
    print "##  pyLoadCore  ##"

    core_err = []

    if sys.version_info > (2, 7):
        core_err.append("Your python version is to new, Please use Python 2.6")

    if sys.version_info < (2, 5):
        core_err.append("Your python version is to old, Please use at least Python 2.5")

    try:
        import pycurl
    except:
        core_err.append("Please install py-curl to use pyLoad.")

    try:
        import Image
    except:
        core_err.append("Please install py-imaging/pil to use Hoster, which uses captchas.")


    pipe = subprocess.PIPE
    try:
        p = subprocess.call(["tesseract"], stdout=pipe, stderr=pipe)
    except:
        core_err.append("Please install tesseract to use Hoster, which uses captchas.")

    try:
        p = subprocess.call(["gocr"], stdout=pipe, stderr=pipe)
    except:
        core_err.append("Install gocr to use some Hoster, which uses captchas.")

    try:
        import OpenSSL
    except:
        core_err.append("Install OpenSSL if you want to create a secure connection to the core.")



    if core_err:
        print "The system check has detected some errors:"
        print ""
        for err in core_err:
            print err
    else:
        print "No Problems detected, pyLoadCore should work fine."


    print ""
    print "##  pyLoadGui  ##"

    gui_err = []

    try:
        import PyQt4
    except:
        gui_err.append("GUI won't work without pyqt4 !!")


    if gui_err:
        print "The system check has detected some errors:"
        print ""
        for err in gui_err:
            print err
    else:
        print "No Problems detected, pyLoadGui should work fine."

    print ""
    print "##  Webinterface  ##"

    web_err = []

    try:
        import django

        if django.VERSION < (1, 1):
            web_err.append("Your django version is to old, please upgrade to django 1.1")
        elif django.VERSION > (1, 2):
            web_err.append("Your django version is to new, please use django 1.1")

    except:
        web_err.append("Webinterface won't work without django !!")



    if not exists(join(dirname(__file__), "module", "web", "pyload.db")):
        web_err.append("You dont have created database yet.")
        web_err.append("Please run: python %s syncdb" % join(dirname(__file__), "module", "web", "manage.py"))



    if web_err:
        print "The system check has detected some errors:"
        print ""
        for err in web_err:
            print err
    else:
        print "No Problems detected, Webinterface should work fine."

if __name__ == "__main__":
    main()

    raw_input("Press Enter to Exit.")