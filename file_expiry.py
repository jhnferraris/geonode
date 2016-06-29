#!/usr/bin/python

import os, os.path, sys, getopt, string, time , logging, math

TARGET_DIR = "/mnt/FTP/PL1/testfolder/DL/geonode_requests"
AGE = 30
PREVIEW_MODE = False
RECURSIVE_MODE = False

def wrong_args_msg():
    print "Wrong or no arguments given."

def help_msg():
    print "Deletes files with age higher than a set age in days. Default is 30 days."
    print "Optional arguments: -d <dir>|--d <dir>| -a <age in days>|--age <age in days>|-p|--preview|-r|--recursive"

def onerror(some_error):
    raise some_error 

class ExpiredFileRemover(object):

    def __init__ (self, log_level="DEBUG"):
        self.log_level = log_level
        self.log = self.log_wrapper()

    def get_files(self, target_dir=TARGET_DIR, age=AGE, recurse=False, preview=True):
        """
        Only removes files, not directories
        """
        file_list = []
        time_lower_limit = time.time() - age* 24 * 60 * 60
        if preview:
            self.log.info("Entering preview mode")
        if recurse:
            for dirName, subDir, fileList in os.walk(target_dir, onerror=onerror):
                    for f in fileList:
                        full_filename = os.path.join(dirName,f)
                        last_modified = os.stat(full_filename).st_mtime
                        self.log.debug("Found file {0} [age:{1} days]...".format(full_filename,
                                                                    math.floor((time.time()-last_modified)/(60*60*24))))
                        if time_lower_limit  > last_modified:
                            if not preview:
                                os.remove(full_filename)
                            self.log.info("Deleted file {0} [age:{1} days]...".format(full_filename,
                                                                    math.floor((time.time()-last_modified)/(60*60*24))))    
                            file_list.append(full_filename)
                                
        else:
            for item in os.listdir(target_dir):
                full_filename = os.path.join(target_dir,item)
                if os.path.isfile(full_filename):
                    last_modified = os.stat(full_filename).st_mtime
                    self.log.debug("Found file {0} [age:{1} days]...".format(full_filename,
                                                                       math.floor((time.time()-last_modified)/(60*60*24))))
                    if time_lower_limit  > last_modified:
                        if not preview:
                            os.remove(full_filename)
                        self.log.info("Deleted file {0} [age:{1} days]...".format(full_filename,
                                                                        math.floor((time.time()-last_modified)/(60*60*24))))
                        file_list.append(full_filename)

        return file_list
            

    def log_wrapper(self):
        """
        Wrapper to set logging parameters for output
        """
        log = logging.getLogger('file_expiry.py')

        # Set the log format and log level
        if self.log_level == "DEBUG":
            log.setLevel(logging.DEBUG)
        elif self.log_level == "INFO":
            log.setLevel(logging.INFO)

        # Set the log format.
        stream = logging.StreamHandler()
        logformat = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%b %d %H:%M:%S')
        stream.setFormatter(logformat)

        log.addHandler(stream)
        return log
        
        

if __name__ == "__main__":
   
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'a:d:hlpr', ["age", "dir","help","live", "preview","recursive"])
    except getopt.GetoptError:
        wrong_args_message()
        help_msg()
        sys.exit(0)
    
    for opt,arg in opts:
        if opt == '-a' or opt=='--age':
            AGE = int(arg)
        elif opt == '-d' or opt == '--dir':
            TARGET_DIR = arg
        elif opt == '-h' or opt == '--help':
            help_msg()
            sys.exit(0)
        elif opt == "-l" or opt == '--live':
            PREVIEW_MODE = False
        elif opt=='-r' or opt=='--recursive':
            RECURSIVE_MODE = True
    
    efr = ExpiredFileRemover(log_level="DEBUG")
    files = efr.get_files(target_dir=TARGET_DIR,age=AGE,recurse=RECURSIVE_MODE, preview=PREVIEW_MODE)
