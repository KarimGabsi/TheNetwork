# -*- coding: utf-8 -*-
import multiprocessing
from multiprocessing import Process, Queue

from TheNetworkGUI import TheNetworkGUI
from TheNetworkP2P import TheNetworkP2P
from TheNetworkLauncher import TheNetworkLauncher
import webbrowser, time
from Utils import Wrapper
from Cluster import Cluster

@Wrapper.Class_Handler(Wrapper.Exception_Handler)
class TheNetwork():
    def __init__(self, gui_ip, gui_port, external_ip, p2p_ip, p2p_port, p2p_cluster):
        self.GUI_IP = gui_ip
        self.GUI_PORT = gui_port
        
        self.EXTERNAL_IP = external_ip
        
        self.P2P_IP = p2p_ip
        self.P2P_PORT = p2p_port
        
        self.P2P_CLUSTER = p2p_cluster
        
        self.GUI_QUEUE = Queue()
        self.P2P_QUEUE = Queue()
    
    def startGUI(self):
        self.GUI_SERVER = Process(target=TheNetworkGUI, args=(self.GUI_IP, self.GUI_PORT, self.GUI_QUEUE, self.P2P_QUEUE,))
        self.GUI_SERVER.name = 'The Network GUI Server'
        self.GUI_SERVER.start()
        print('DO NOT CLOSE WINDOW UNLESS APPLICATION IS NOT NEEDED ANYMORE')
#        time.sleep(1) #Wait a second before opening the browser 
#        webbrowser.open('http://{0}:{1}/'.format(self.GUI_IP, self.GUI_PORT))
    
    def startP2P(self):
        self.P2P_SERVER = Process(target=TheNetworkP2P, args=(
                self.P2P_IP,
                self.P2P_PORT,
                self.EXTERNAL_IP,
                self.GUI_QUEUE,
                self.P2P_QUEUE,
                self.P2P_CLUSTER,))
        self.P2P_SERVER.name = 'The Network P2P'
        self.P2P_SERVER.start()
        print('P2P Started')
           
def main():
    #Clear Log
    Wrapper.Clear_Log()
    
    #Start Launcher
    launcher = TheNetworkLauncher()
    launcher.Launch()
    while launcher.active:
        pass
    
    #Establish the network
    print('Done: ', launcher.GUI_IP, launcher.GUI_PORT, launcher.P2P_IP, launcher.P2P_PORT)
    print('Cluster Path: ', launcher.CLUSTER_PATH)
    
    #Read Cluster file
    cluster = Cluster(launcher.CLUSTER_PATH)
    print(cluster.key)
    print(cluster.peers)
    
    #Start GUI then P2P
    thenetwork = TheNetwork(launcher.GUI_IP,
                            launcher.GUI_PORT,
                            launcher.EXTERNAL_IP,
                            launcher.P2P_IP, 
                            launcher.P2P_PORT,
                            cluster)
    thenetwork.startGUI()
    thenetwork.startP2P()
    
if __name__ == '__main__':
    __spec__ = "ModuleSpec(name='builtins', loader=<class '_frozen_importlib.BuiltinImporter'>)"
    #Pyinstallerfix
    multiprocessing.freeze_support()
    main()