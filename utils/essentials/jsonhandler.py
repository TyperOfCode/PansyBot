
import os
import json

class js:
    class config:
        def __init__(self, filepath, log=False):
            if not filepath.endswith('.json'):
                raise ValueError(f'Json Handler: File does not end with .json : {filepath}')
                return
            

            if not os.path.exists(filepath):
                try:
                    x = open(filepath,'w')
                except:
                    raise ValueError(f'Json Handler: Path does not exist : {filepath}')
                    return

            self.fp = filepath
            self.log = log

        def __logprint(self,message):
            if self.log:
                print('[LOGPRINT]>> '+message,end='\n---------------\n\n')

        def grab(self):
            self.__logprint(f'Grab initiated. Filename: {self.fp}')
            try:
                self.__logprint(f'Grab started.. from file: {self.fp}')
                with open(self.fp,'r') as readfile:
                    data = json.load(readfile)
                    self.__logprint(f'[Success] Grabbed data from file: {self.fp}')
                    return data
            except json.JSONDecodeError:
                self.__logprint(f'Exception occured, decode error, ignoring --- returning empty dict')
                return {}
            except Exception as e:
                self.__logprint(f'Exeception occured in grab: {e}')
                raise ValueError('Json Handler: Error grabbing from file %s | Deleted?'%(self.fp))
                return {}

        
        def write(self, data, indent = 4):
            self.__logprint(f'Write initiated. Filename: {self.fp} Indent: {indent}  data: [{data}]\n')
            try:
                with open(self.fp,'w') as writefile:
                    old = self.grab()
                    try:
                        self.__logprint(f'Dumping data to file: {self.fp}')
                        json.dump(data,writefile, indent=indent)
                        self.__logprint(f'[Success] Dumped data to file: {self.fp}')
                    except:
                        json.dump(old, writefile, 4)
                        raise ValueError
           

            except Exception as e:
                self.__logprint(f'Exception occured in write: {e}')
                raise ValueError('Json Handler: Error writing to file %s | Deleted? (data reverted)'%(self.fp))
                return False
            return True

        

        def printwholestruct(self,data=None):
            if data == None:
                data = self.grab()

            def recurprint(data,prev,times):
                for i in data[prev]:
                    
                    if type(data[prev][i]) == dict:
                        print('{}L '.format(" " * times) + i)
                        recurprint(data[prev],i,times + 1)
                    else:
                        print("{}L {} : {}".format(" " * times,str(i),str(data[prev][i])))

            for i in data:
                print(i)
                recurprint(data,i,1)
        
       



        



            

            