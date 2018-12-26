import os
import shutil

from Environment import Environment 

class Maintenance:
    def UpdateVersionLocal():
        my_dir= Environment.getMyFolder()
        src = my_dir + '/next'
        src_files = os.listdir(src)
        dest = my_dir
        for file_name in src_files:
            full_file_name = os.path.join(src, file_name)
            if (os.path.isfile(full_file_name)):
                shutil.copy(full_file_name, dest)
        for file_name in src_files:
            full_file_name = os.path.join(src, file_name)
            if (os.path.isfile(full_file_name)):
                os.remove(full_file_name)
