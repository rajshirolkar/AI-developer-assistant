import os
import csv
import datetime
from . import eval_copilot_log_utils

class eval_copilot_log:
    def __init__(self,auto_flush=True):
        self.directory="./log/out"
        self._init_path()
        self.auto_flush=auto_flush
        self.log=[]
        self.waitfor_thumb=False



    def _init_path(self):
        os.makedirs(self.directory,exist_ok=True)
        now_time = datetime.datetime.now()
        self.log_file_path=now_time.strftime("%Y%m%d-%H%M%S")+".csv"


    def save_dict_log(self,file_name,dict_log):
        dict_log[0]["thumb"]=""
        keywords=dict_log[0].keys()

        file_path=os.path.join(self.directory,file_name)
        file_exists=os.path.isfile(file_path)

        with open(file_path,"a",newline='') as f:
            writer=csv.DictWriter(f,fieldnames=keywords)

            if not file_exists:
                writer.writeheader()

            for row in dict_log:
                writer.writerow(row)


    def add_line(self,data):
        if self.auto_flush:
            self.log=[data]
            self.save_dict_log(self.log_file_path,self.log)
            self.waitfor_thumb=True
        else:
            print("Error: auto_flush is set to False, not implemented yet")

    def add_thumb(self,thumb):
        if self.waitfor_thumb:
            eval_copilot_log_utils.append_thumb(os.path.join(self.directory,self.log_file_path),thumb)
            self.waitfor_thumb=False
        else:
            print("Warning: (ignoring action) add_thumb called without previous add_line")



if __name__=="__main__":
    log=eval_copilot_log()
    log.add_line({"a":1,"b":2,"c":3})
    log.add_line({"a": 1, "b": 2, "d": 3})



