from shutil import copyfile
import os
    
def importModulesAndSetup():
    import pynoddy
    
    ##############
    # Some file fixes
    ##############
    basepynoddyfile = pynoddy.__file__[:-11]+'experiment/__init__.py'
    # Read in the file
    with open(basepynoddyfile, 'r') as file :
      filedata = file.read()

    # Replace the target string
    filedata = filedata.replace('from . import util.sampling as Sample', 'from .util import sampling as Sample')

    # Write the file out again
    with open(basepynoddyfile, 'w') as file:
      file.write(filedata)

    target = pynoddy.__file__[:-11]+'output.py'

    source = 'output.py'

    copyfile(source, target)

    target = pynoddy.__file__[:-11]+'events.py'

    source = 'events.py'

    copyfile(source, target)

    ##############
    # Changing exection permissions
    ##############
    folder = os.getcwd()
    noddyEXE = folder+'/noddy.exe'
    strV = 'chmod 777 '+noddyEXE
    os.system(strV)
    import pynoddy.experiment