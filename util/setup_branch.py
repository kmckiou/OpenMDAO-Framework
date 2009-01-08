
import os
import sys
import shutil
import platform
from os.path import join, normpath
from optparse import OptionParser
from subprocess import Popen,PIPE,STDOUT

#MDAO_HOME = join(normpath('/OpenMDAO'),'dev')
MDAO_HOME = join(normpath('/home/bnaylor/OpenMDAO'),'dev')

# TODO: fix the real directory structure such that
# developer branches live under /OpenMDAO/dev/developers
BRANCHES_HOME = join(MDAO_HOME,'developers')

options = None


def error_out(msg):
    print >> sys.stderr, msg
    sys.exit(-1)

def run_command(cmd, sh=True):
   """Run a command using Popen and return its output (stdout and stderr)
   and its return code as a tuple. If the command is a python file, prepend
   python to the command string
   """
#   p = Popen(cmd, stdout=PIPE, stderr=STDOUT, env=os.environ, shell=sh)
   p = Popen(cmd, env=os.environ, shell=sh)
   output = p.communicate()[0]
   return (output, p.returncode)

   
def make_branch_name(ticket, desc):
    name = 'T'+str(ticket)
    if desc is not None and desc != '':
        name += '-'+desc
    return name

def make_virtual_dir():
    virt_dir = 'virtual'
    
    # tell virtualenv to create a virtual environment in the 'virtual'
    # directory
    output, retcode = run_command('virtualenv --no-site-packages '+virt_dir)   
    if retcode != 0:
        error_out("error creating virtual environment")
    os.chdir(virt_dir) 
        
    make_buildout_dir()


def make_buildout_dir():  
    global options
      
    # activate the virtual python environment
    activate_file = join(os.getcwd(), 'bin', 'activate_this.py')
    execfile(activate_file, dict(__file__=activate_file))
    
    os.makedirs('buildout')
    os.chdir('buildout')
    
    # grab the buildout bootstrap file
    shutil.copy('../../util/branch_config/bootstrap.py', 'bootstrap.py')
    
    # grab the buildout configuration file
    if options.buildout:
        shutil.copy(options.buildout, 'buildout.cfg')
    else:
        shutil.copy('../../util/branch_config/buildout.cfg', 'buildout.cfg')
    
    # bootstrap our buildout
    output, retcode = run_command(join('..','bin','python')+' bootstrap.py')   
    if retcode != 0:
        error_out("error bootstrapping buildout")
    output, retcode = run_command(join('bin','buildout'))  
    if retcode != 0:
        error_out("error running buildout")
    

    
def create_branch(src_branch, new_branch):
    if not os.path.isdir(src_branch):
        error_out("can't find source branch '"+src_branch+"'")
        
    if os.path.isdir(join(os.getcwd(), new_branch)):
        error_out("branch '"+join(os.getcwd(), new_branch)+
                           "' already exists")
        
    cmd = 'bzr branch '+src_branch+' '+new_branch
    output, retcode = run_command(cmd)
    
    if retcode != 0:
        error_out("error creating bazaar branch '"+new_branch+"'")
    

def main():
    """ process args from command line """

    global options
   
    parser = OptionParser()
    parser.add_option("-u","", action="store", type="string", dest="user",
                      help="username (defaults to value of LOGNAME "+
                      "environment variable)")
    parser.add_option("-s","", action="store", 
                      type="string", dest="source",
                      help="full path of source branch (defaults to trunk path)")
    parser.add_option("-t","", action="store", 
                      type="int", dest="ticket",
                      help="ticket number for new branch")
    parser.add_option("-d","", action="store", 
                      type="string", dest="desc",help="short "+
                      "(<15 character) description of the new branch")
    parser.add_option("-b","", action="store", type="string", dest="buildout",
                      help="specify a buildout.cfg file")
                        
    (options, args) = parser.parse_args(sys.argv[1:])
   
    if options.user:
        username = options.user
    else:
        username = os.environ['LOGNAME']
        
    if options.ticket:
        ticket = options.ticket
        if ticket < 0:
            error_out('Invalid ticket number ('+str(options.ticket)+')')
    else:
        parser.print_help()
        error_out('Ticket number for new branch is mandatory')
        
    if options.desc:
        desc = options.desc
    else:
        desc = ''
        
    if options.source:
        src_branch = options.source
    else:
        src_branch = join(MDAO_HOME,'trunk')
      
    new_branch = make_branch_name(ticket, desc)
    
    start_path = os.getcwd()
    
    os.chdir(join(BRANCHES_HOME,username))
    
    create_branch(src_branch, new_branch)
    
    # cd to the top of the new branch
    os.chdir(new_branch)
    
    make_virtual_dir()
    

if __name__ == '__main__':
    main()
