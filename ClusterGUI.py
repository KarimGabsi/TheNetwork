# -*- coding: utf-8 -*-
from tkinter import Tk, Label, Entry, Button, StringVar, filedialog, Listbox
from tkinter.messagebox import showinfo
from tkinter import simpledialog
from PIL import ImageTk, Image
import os

#TODO
#1) CHECK IP FORMAT
#3) SHOW ERRORS USING SHOWINFO
#4) CREATE CLUSTER FILE
class ClusterGUI():
    def __init__(self):
        self.CLUSTER_PATH = None
        self.key = None
        self.peers = []
        
    
    def addpeer(self):
        ip = simpledialog.askstring("Add peer", "IP address to add? {xxx.xxx.xxx.xxx}",
                                parent=self.root)
        
        if ip is not None:
            port = simpledialog.askinteger("Add port", "Corresponding port? 1 <= port => 65535",
                                parent=self.root,
                                minvalue=1, maxvalue=65535)
            if port is not None:
                self.peers.append((ip, port))
                
        self.refreshpeers()
    
    def removepeer(self):
        cs = self.CLUSTER_PEERS_listbox.curselection()
        for index in reversed(cs):
            del self.peers[index]
        
        self.refreshpeers()
     
    def refreshpeers(self):
        self.CLUSTER_PEERS_listbox.delete(0, 'end')
        i = 1
        for peer, ip in self.peers:
            self.CLUSTER_PEERS_listbox.insert(i, '{0}:{1}'.format(peer, ip))
            i+= 1
            
    def create(self):
        self.root.destroy()
        
    def browsercluster(self):
        file = filedialog.asksaveasfile(mode='w', defaultextension=".tnc")
        if file != None:
            self.CLUSTER_PATH_VAR.set(file.name)
            file.close()
            os.remove(file.name)         
        else:
            return

    def launch(self):
        self.root = Tk()
        self.root.resizable(width=False, height=False)
        self.root.winfo_toplevel().title('The Network')
        self.root.iconbitmap('GUI/favicon.ico')
        self.root.configure(background='black')
        
        window_width = 800
        window_height = 400
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()    
        x_cordinate = int((screen_width/2) - (window_width/2))
        y_cordinate = int((screen_height/2) - (window_height/2))
        
        self.root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
        
        img = ImageTk.PhotoImage(Image.open("GUI/img/eye.png"))
        logo = Label(self.root, image = img, background='black')
        
        GUI_label = Label(self.root, text='CLUSTER CREATION', background='black', foreground='white')
        
        CLUSTER_label = Label(self.root, text='CLUSTER (*.tnc): ', background='black', foreground='white')
        self.CLUSTER_PATH_VAR = StringVar(self.root, value=self.CLUSTER_PATH)
        CLUSTER_entry = Entry(self.root, textvariable=self.CLUSTER_PATH_VAR, width=60)
#
        CLUSTER_browse = Button(self.root, text='Browse', command=self.browsercluster)
        self.CREATE_button = Button(self.root, text='Create', command=self.create)
        
        CLUSTER_PEERS_label = Label(self.root, text='CLUSTER PEERS: ', background='black', foreground='white')
        self.CLUSTER_PEERS_listbox = Listbox(self.root, width = 50, height = 5)
        CLUSTER_PEERS_add = Button(self.root, text='Add', command=self.addpeer)
        CLUSTER_PEERS_remove = Button(self.root, text='Remove', command = self.removepeer)

        self.peers.append(('127.0.0.1',8080))
        self.peers.append(('127.0.0.1',9999))
        self.peers.append(('127.0.0.1',1234))
        self.refreshpeers()

        #Grid
        logo.grid(row = 0, column = 0, rowspan = 4)
        GUI_label.grid(row = 0, column = 1, columnspan=10)   
        
        CLUSTER_label.grid(row=1, column = 1)
        CLUSTER_entry.grid(row=1, column = 2, columnspan = 6)
        CLUSTER_browse.grid(row=1, column = 8, sticky = 'nsew')
        
        CLUSTER_PEERS_label.grid(row = 3, column = 1, rowspan = 2)
        self.CLUSTER_PEERS_listbox .grid(row = 3, column = 2, columnspan = 6, rowspan = 2)
        CLUSTER_PEERS_add.grid(row = 3, column = 8, sticky = 'nsew')
        CLUSTER_PEERS_remove.grid(row = 4, column = 8, sticky = 'nsew')
        
        self.CREATE_button.grid(row = 5, column = 2, columnspan = 6, sticky = 'nsew')
        
        self.root.mainloop()

if __name__ == "__main__":
    cGUI = ClusterGUI()
    cGUI.launch()