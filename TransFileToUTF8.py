#-*- coding: utf-8 -*-

import codecs
import os
import shutil
import re
import chardet
import zipfile
import time

def process_bak_files(action='restore'):
    log_file = open('log.txt', 'w')
    for filename in os.listdir('.'):
        if filename.lower().endswith('.as'):
            try:
                if action == 'restore':
                    shutil.copy(filename, filename + '.bak')
                elif action == 'clear':
                    os.remove(filename)
            except Exception, e:
                log_file.write('backup error: ' + e + '\r\n')
                log_file.close()
                
    log_file.close()


"""
def process_bak_files(action='restore'):
    for root, dirs, files in os.walk(os.getcwd()):
        for f in files:
            if f.lower().endswith('.as.bak'):
                source = os.path.join(root, f)
                target = os.path.join(root, re.sub('\.java\.bak$', '.java', f, flags=re.IGNORECASE))
                try:
                    if action == 'restore':
                        shutil.move(source, target)
                    elif action == 'clear':
                        os.remove(source)
                except Exception, e:
                    print source
"""


def convert_encoding(filename, target_encoding, log_list):
    # Backup the origin file.
    # shutil.copyfile(filename, filename + '.bak')

    # convert file from the source encoding to target encoding
    content = codecs.open(filename, 'r').read()
    file_encoding = chardet.detect(content)['encoding']

    if 'utf-8' != file_encoding.lower():
        content = content.decode(file_encoding)
        #.encode(source_encoding)
        codecs.open(filename, 'w', encoding=target_encoding).write(content)

        # print file info, write to log file
        str_log = 'Succeed! ' + filename + ': ' + file_encoding + '\r\n'
        log_list.append(str_log)        
    else:
        str_log = '---------Attention:' + filename + 'code is utf-8----------\r\n'
        log_list.append(str_log)


def convert_all_as_files():
    log_file = open('log.txt', 'w')
    for filename in os.listdir('.'):
        if filename.lower().endswith('.as'):
            try:
                log_list = []                
                convert_encoding(filename, 'utf-8', log_list)                
                for log in log_list:                    
                    log_file.write(log)                
            except Exception, e:                
                str_log = '---------Error: convert ' + filename + ' failed!----------\r\n' \
                           + 'exceptoin info:' + e + '\r\n'
                log_file.write(str_log)
                log_file.close()
   
    log_file.close()


def compress_as_files():
    zip_file_name = 'ClientProto_' + time.strftime('%Y-%m-%d %H_%M_%S', time.localtime()) + '.zip'    
    zip_file = zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED)
    for filename in os.listdir('.'):
        if filename.lower().endswith('.as'):
            zip_file.write(filename)

    zip_file.close()


def copy_hpp_files(source_dir, target_dir):
    log_file = open('log.txt', 'a')
    for filename in os.listdir(source_dir):
        if filename.lower().endswith('.h'):
            try:                
                shutil.copy(source_dir + filename, target_dir + filename)
                str_log = 'OK! copy ' + source_dir + filename + ' to ' \
                           + target_dir + filename + '\r\n'
                log_file.write(str_log)
            except Exception, e:                
                str_log = '---------Error: copy ' + filename + ' failed!----------\r\n' \
                           + 'exceptoin info:' + e + '\r\n'
                log_file.write(str_log)
                log_file.close()                

    log_file.close()
                
    
def main():

    #
    convert_all_as_files()   

    #compress all as files
    compress_as_files()

    #'..\ProtoServer\*.h', '..\..\Server\Framework\Src\CommInclude\LogicPacket\'
    source_dir = '..\\ProtoServer\\'
    target_dir = '..\\..\\Server\\Framework\\Src\\CommInclude\\LogicPacket\\'   
    copy_hpp_files(source_dir, target_dir)


if __name__ == '__main__':

    cur_dir = os.getcwd()
    os.chdir('..')
    
    #process_bak_files()
    main()    
   
    os.chdir(cur_dir)
    #os.system('pause')
