import os
import time
import subprocess
import psutil
from datetime import datetime


class RunProcess:
    pid = None
    args = None
    proc = None

    def __init__(self, args):
        self.args = args

    def run(self):
        self.proc = subprocess.Popen(self.args)
        self.pid = self.proc.pid
        return self.pid

    def is_run(self):
        if self.proc is not None and self.proc.poll() is None:
            return True
        else:
            return False


class Statistics:
    pid = None
    proc = None
    stat_time = None
    proc_info = None
    info_fields = None
    os_type = None

    def __init__(self, pid):
        self.pid = pid
        self.proc = psutil.Process(proc.pid)
        self.check_os()

    def check_os(self):
        if hasattr(self.proc, 'num_handles'):
            self.os_type = 'win'
            self.info_fields = ['CPU Load', 'Working Set', 'Private Bytes', 'Open Handles']
        else:
            self.os_type = 'unix'
            self.info_fields = ['CPU Load', 'Resident Set Size', 'Virtual Memory Size',
                                'Open File Descriptors']
        self.proc_info = [0]*len(self.info_fields)

    def get_cpu_load(self):
        self.proc_info[0] = self.proc.cpu_percent()

    def get_memory_info(self):
        mem = self.proc.memory_info()
        if self.os_type == 'win':
            self.proc_info[1] = mem.rss
            self.proc_info[2] = mem.private
        else:
            self.proc_info[1] = mem.rss
            self.proc_info[2] = mem.vms

    def get_fds(self):
        if self.os_type == 'win':
            self.proc_info[3] = self.proc.num_handles()
        else:
            self.proc_info[3] = self.proc.num_fds()

    def get_stat(self):
        try:
            self.stat_time = datetime.now()
            self.get_cpu_load()
            self.get_memory_info()
            self.get_fds()
            return True
        except psutil.NoSuchProcess:
            return False

    def get_fields(self):
        return ';'.join(['Datetime'] + self.info_fields)

    def __str__(self):
        return '{};{:.2f}%;{};{};{}'.format(self.stat_time.strftime('%Y-%m-%d %H:%M:%S'), *self.proc_info)


class Log:
    filename = None
    file = None

    def __init__(self, filename, header=None):
        self.filename = filename
        self.openfile()
        if header is not None and header != '':
            self.write(header)

    def openfile(self):
        self.file = open(self.filename, 'w')

    def write(self, text):
        self.file.write(text + '\n')

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file is not None:
            self.file.close()
            self.file = None
        return False


if __name__ == '__main__':
    print('Введите путь к процессу')
    process_path = input()
    if os.path.isfile(process_path):
        print('Введите интервал')
        try:
            interval = int(input())
        except ValueError:
            interval = 0
        if interval > 0:
            proc = RunProcess(process_path)
            try:
                proc.run()
            except OSError:
                print('Файл невозможно запустить')
            if proc.pid is not None:
                stat = Statistics(proc.pid)
                log = Log('GetProcessStat.csv', stat.get_fields())
                while proc.is_run():
                    start_time = time.time()
                    if stat.get_stat():
                        log.write(str(stat))
                        time.sleep(interval - (time.time()-start_time) % interval)
                    else:
                        print('Process closed')
        else:
            print('Интервал должен быть больше 0')
    else:
        print('Указанный файл не существует')
