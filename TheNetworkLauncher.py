# -*- coding: utf-8 -*-
from tkinter import Tk, Label, Entry, Button, StringVar, filedialog
from tkinter.messagebox import showinfo
from PIL import ImageTk, Image
from configparser import RawConfigParser
from Utils import IPConfig, TestConnection

import os, socket
class TheNetworkLauncher():
    def __init__(self):
        self.active = True
        self.EXTERNAL_IP = IPConfig().getexternalip()
        self.cp = RawConfigParser()
        self.cfile = 'TheNetwork.config'
        self.ReadConfig()
        
    def ReadConfig(self):
        if os.path.isfile(self.cfile):
            self.cp.read(self.cfile)
        else:
            self.WriteConfig()
            self.ReadConfig()
        
        self.GUI_IP = self.cp.get('IP CONFIG', 'GUI_IP')
        if not self.GUI_IP:
            self.GUI_IP = '127.0.0.1'
            
        self.GUI_PORT = int(self.cp.get('IP CONFIG', 'GUI_PORT'))
        if not self.GUI_PORT:
            self.GUI_PORT = 1919
            
        self.P2P_IP = self.cp.get('IP CONFIG', 'P2P_IP')
        if not self.P2P_IP:
            self.P2P_IP = IPConfig().getlocalip()
            
        self.P2P_PORT = int(self.cp.get('IP CONFIG', 'P2P_PORT'))
        if not self.P2P_PORT:
            self.P2P_PORT = 4319
            
        self.CLUSTER_PATH = self.cp.get('CLUSTER', 'PATH')
        if not self.CLUSTER_PATH:
            self.CLUSTER_PATH = os.path.join(os.getcwd(), 'Cluster', 'global.tnc')

    def WriteConfig(self, gui_ip='', gui_port='', p2p_ip='', p2p_port='', cluster_path=''):
        
        if not self.cp.has_section('IP CONFIG'):
            self.cp.add_section('IP CONFIG')
        self.cp['IP CONFIG']['GUI_IP'] = gui_ip
        self.cp['IP CONFIG']['GUI_PORT'] = gui_port
        self.cp['IP CONFIG']['P2P_IP'] = p2p_ip
        self.cp['IP CONFIG']['P2P_PORT'] = p2p_port
        
        if not self.cp.has_section('CLUSTER'):
            self.cp.add_section('CLUSTER')
        self.cp['CLUSTER']['PATH'] = cluster_path
        
        with open(self.cfile, 'w') as file:
            self.cp.write(file)
    
    def BrowseCluster(self):
        file = filedialog.askopenfile(parent=self.root,mode='rb',title='Choose a cluster file')
        if file != None:
            self.CLUSTER_PATH_VAR.set(file.name)
            file.close()
    
    def Connect(self):
        self.CONNECT_button['state'] = 'disabled'
        if self.CheckInput():
            print(self.P2P_IP_VAR.get(), self.EXTERNAL_IP, int(self.P2P_PORT_VAR.get()))
            tc = TestConnection(self.P2P_IP_VAR.get(), self.EXTERNAL_IP, int(self.P2P_PORT_VAR.get()), timeout=5)
            if tc.isOnline:
                self.WriteConfig(
                        self.GUI_IP_VAR.get(),
                        self.GUI_PORT_VAR.get(),
                        self.P2P_IP_VAR.get(),
                        self.P2P_PORT_VAR.get(),
                        self.CLUSTER_PATH_VAR.get())
                self.ReadConfig() #Read again for later calling...
                self.root.destroy()
                self.active = False
            else:
                showinfo("Window", "Cannot open a connection with given parameters")
                self.CONNECT_button['state'] = 'normal'
        else:
            self.CONNECT_button['state'] = 'normal'
    
    def CheckInput(self):
        if self.GUI_IP_VAR.get():
            try:
                socket.inet_pton(socket.AF_INET, self.GUI_IP_VAR.get())
            except:
                showinfo("Window", "Invalid GUI IP")
                return False
        
        if self.P2P_IP_VAR.get():
            try:
                socket.inet_pton(socket.AF_INET, self.P2P_IP_VAR.get())
            except:
                showinfo("Window", "Invalid P2P IP")
                return False
        
        if self.GUI_PORT_VAR.get():
            if self.GUI_PORT_VAR.get().isdigit() and (1 <= int(self.GUI_PORT_VAR.get()) <= 65535):
                pass
            else:
                showinfo("Window", "Invalid GUI PORT")
                return False
        
        if self.GUI_PORT_VAR.get():
            if self.P2P_PORT_VAR.get().isdigit() and (1 <= int(self.P2P_PORT_VAR.get()) <= 65535):
                pass
            else:
                showinfo("Window", "Invalid P2P PORT")
                return False
        
        if not os.path.exists(self.CLUSTER_PATH_VAR.get()):
            showinfo("Window", "Invalid CLUSTER PATH")
            return False
        
        return True
    def Launch(self):
        self.root = Tk()
        self.root.resizable(width=False, height=False)
        self.root.winfo_toplevel().title('The Network')
        self.root.iconbitmap('GUI/favicon.ico')
        self.root.configure(background='black')
        
        window_width = 600
        window_height = 225
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()    
        x_cordinate = int((screen_width/2) - (window_width/2))
        y_cordinate = int((screen_height/2) - (window_height/2))
        
        self.root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
        
        img = ImageTk.PhotoImage(Image.open("GUI/img/eye.png"))
        logo = Label(self.root, image = img, background='black')
        
        GUI_label = Label(self.root, text='GUI CONFIGURATION (empty for default)', background='black', foreground='white')
        
        GUI_host_label = Label(self.root, text='IP: ', background='black', foreground='white')
        self.GUI_IP_VAR = StringVar(self.root, value=self.GUI_IP)
        GUI_host_entry = Entry(self.root, textvariable=self.GUI_IP_VAR)
        
        GUI_port_label = Label(self.root, text=' PORT: ', background='black', foreground='white')
        self.GUI_PORT_VAR = StringVar(self.root, value=self.GUI_PORT)
        GUI_port_entry = Entry(self.root, textvariable=self.GUI_PORT_VAR)
        
        P2P_label = Label(self.root, text='P2P CONFIGURATION (empty for default)', background='black', foreground='white')
        
        P2P_host_label = Label(self.root, text='IP: ', background='black', foreground='white')
        self.P2P_IP_VAR = StringVar(self.root, value=self.P2P_IP)
        P2P_host_entry = Entry(self.root, textvariable=self.P2P_IP_VAR)
        
        P2P_port_label = Label(self.root, text=' PORT:', background='black', foreground='white')
        self.P2P_PORT_VAR = StringVar(self.root, value=self.P2P_PORT)
        P2P_port_entry = Entry(self.root, textvariable=self.P2P_PORT_VAR)
        
        CLUSTER_label = Label(self.root, text='CLUSTER: ', background='black', foreground='white')
        self.CLUSTER_PATH_VAR = StringVar(self.root, value=self.CLUSTER_PATH)
        CLUSTER_entry = Entry(self.root, textvariable=self.CLUSTER_PATH_VAR)

        CLUSTER_browse = Button(self.root, text='Browse', command=self.BrowseCluster)
        self.CONNECT_button = Button(self.root, text='Connect', command=self.Connect)
        
        #GRID
        logo.grid(row = 0, column = 0, rowspan = 8)
        
        GUI_label.grid(row = 0, column = 1, columnspan = 5)
        GUI_host_label.grid(row = 1, column = 2)
        GUI_host_entry.grid(row = 1, column = 3)
        GUI_port_label.grid(row = 1, column = 4)
        GUI_port_entry.grid(row = 1, column = 5)
        
        P2P_label.grid(row = 2, column = 1, columnspan = 5)
        P2P_host_label.grid(row = 3, column = 2)
        P2P_host_entry.grid(row = 3, column = 3)
        P2P_port_label.grid(row = 3, column = 4)
        P2P_port_entry.grid(row = 3, column = 5)
        
        CLUSTER_label.grid(row=4, column = 1, columnspan = 2)
        CLUSTER_entry.grid(row=4, column = 3, columnspan = 2)
        CLUSTER_browse.grid(row=4, column = 5, sticky = 'nsew')
        self.CONNECT_button.grid(row = 6, column = 2, columnspan = 5, sticky = 'nsew')
        
        self.root.mainloop()