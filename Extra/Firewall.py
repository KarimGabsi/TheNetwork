# -*- coding: utf-8 -*-
import ctypes, sys
from subprocess import PIPE, run

class Firewall():
    def __init__(self, rulename, protocol, port, _dict):
        self.rulename = rulename
        self.protocol = protocol
        self.port = port
        self.dict = _dict
        
        self.run_as_admin()        
        self.config()
        
    def run_as_admin(self):
        """ Force to start application with admin rights """
        try:
            isAdmin = ctypes.windll.shell32.IsUserAnAdmin()
        except AttributeError:
            isAdmin = False
        if not isAdmin:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
            sys.exit(0)
    
    def check_rule(self, rule_name, bound):
        command = f"netsh advfirewall firewall show rule name=\"{rule_name}\" dir=\"{bound}\""
        return self.do_command(command)
    
    def add_rule(self, rule_name, bound, protocol, port):
        command = f"netsh advfirewall firewall add rule name=\"{rule_name}\" dir=\"{bound}\" action=allow protocol=\"{protocol}\" localport=\"{port}\" remoteport=\"{port}\""
        return self.do_command(command)
    
    def remove_rule(self, rule_name, bound):
        command = f"netsh advfirewall firewall delete rule name=\"{rule_name}\" dir=\"{bound}\""
        return self.do_command(command)
    
    def set_rule(self, rule_name, bound, protocol, port):
        command = f"netsh advfirewall firewall set rule name=\"{rule_name}\" dir=\"{bound}\" new protocol=\"{protocol}\" localport=\"{port}\" remoteport=\"{port}\""
        return self.do_command(command)
    
    def do_command(self, command):
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        print(result.stdout)
        if result.returncode == 0:
            return True
        else:
            return False
    
    def config(self):
        #INBOUND
        print('Checking inbound rule')
        if self.check_rule(self.rulename, 'in'):
            print('Modifying inbound rule')
            self.set_rule(self.rulename, 'in', self.protocol, self.port)
        else:
            print('Adding inbound rule')
            self.add_rule(self.rulename, 'in', self.protocol, self.port)
            
        #OUTBOUND
        print('Checking outbound rule')
        if self.check_rule(self.rulename, 'out'):
            print('Modifying outbound rule')
            self.set_rule(self.rulename, 'out', self.protocol, self.port)
        else:
            print('Adding outbound rule')
            self.add_rule(self.rulename, 'out', self.protocol, self.port)
        
        self.dict['READY'] = True
        
if __name__ == '__main__':
    __spec__ = "ModuleSpec(name='builtins', loader=<class '_frozen_importlib.BuiltinImporter'>)"
    import multiprocessing
    from multiprocessing import Process, Manager
    multiprocessing.freeze_support()
    rulename = 'The Network P2P'
    protocol = 'TCP'
    port = 3812
    manager = Manager()
    dic = manager.dict()
    dic['READY'] = False
    pfirewall = Process(target=Firewall, args=(rulename, protocol, port, dic,))
    pfirewall.name = 'The Network Firewall Config'
    pfirewall.start()
    pfirewall.join()
      
    if dic['READY']:
        print('Rock n Roll')
    else:
        print('Shit ain\'t getting through...')
            
    input('press to exit...')
    
    