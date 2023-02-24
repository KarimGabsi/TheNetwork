# -*- coding: utf-8 -*-
from flask import Flask, render_template, send_from_directory, request, jsonify
import bisect, time
from Utils import MyEncoder, Message, Wrapper, IPConfig
import webbrowser
import threading

@Wrapper.Class_Handler(Wrapper.Exception_Handler)
class TheNetworkGUI():
    def __init__(self, host, port, gui_queue, p2p_queue):
        self.app = Flask(__name__, template_folder='GUI', static_url_path='/')
        self.app.secret_key = 'TemetNosce'
        self.host = host
        self.port = port
        self.messages = [Message('hi', '123.456.789'), Message('hi back', '127.0.0.1')]
        
        self.gui_queue = gui_queue
        self.p2p_queue = p2p_queue
        self.gui_queue_thread = threading.Thread(target=lambda: self.repeat(self.manageGUIQueue)).start()
        
        self.externalip = IPConfig().getexternalip()
        
        @self.app.route('/', methods=['GET', 'POST'])
        def home():
            return render_template('index.html')

        @self.app.route('/<path:path>')
        def sendfile(path): 
            return send_from_directory('GUI', '{0}'.format(path))
        
        @self.app.route('/fetchmessages', methods=['GET'])
        def fetchmessages():
            message = next(iter(self.messages), None)
            if message != None:
                self.messages.remove(message)
            return jsonify(MyEncoder().encode(message))
        
        @self.app.route('/broadcastmessage', methods=['POST'])
        def broadcastmessage():
#            myMessage = Message(request.form['message'], request.form['ip'])
            myMessage = Message(request.form['message'], self.externalip)
            self.onMessageSend(myMessage)
            return jsonify(MyEncoder().encode(myMessage)), 200
            
        @self.app.route('/action/<actiontype>', methods=['POST'])
        def action(actiontype):
            webbrowser.open('http://www.google.com')
            return 'You started the action: {0}'.format(actiontype)
        
        self.app.run(self.host, self.port, False)
        
    def onMessageReceived(self, message):
        bisect.insort(self.messages, message)
    
    def onMessageSend(self, message):
        self.p2p_queue.put(('send_message', message))
    
    def manageGUIQueue(self):
        if not self.gui_queue.empty():
            item = self.gui_queue.get()
            function = item[0]
            args = item[1:]
            if function.lower() == 'receive_message':
                self.onMessageReceived(args[0])
            #print('function: ', function, 'args: ', args)
            #function(self, *args)
        
    def repeat(self, task, delay=0):
        while True:
            if not delay == 0:
                time.sleep(delay)
            task()