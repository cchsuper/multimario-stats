import socket
import datetime

class ChatRoom:
    def __init__(self, channel, nick, password):
        self.HOST = "irc.chat.twitch.tv"
        self.PORT = 6667
        self.NICK = nick
        self.PASSWORD = password
        self.channel = channel
        self.currentSocket = socket.socket()
        self.inputBuffer = ""
        self.reconnect()
    def message(self, msg):
        try:
            self.currentSocket.send(bytes("PRIVMSG "+self.channel+" :"+msg+"\n", "UTF-8"))
        except socket.error:
            print("[Twitch IRC] Socket error.")
    def reconnect(self):
        self.currentSocket = socket.socket()
        self.currentSocket.connect((self.HOST,self.PORT))
        self.currentSocket.send(bytes("PASS "+self.PASSWORD+"\n", "UTF-8"))
        self.currentSocket.send(bytes("NICK "+self.NICK+"\n", "UTF-8"))
        self.currentSocket.send(bytes("JOIN "+self.channel+"\n", "UTF-8"))
        self.currentSocket.send(bytes("CAP REQ :twitch.tv/tags twitch.tv/commands\n", "UTF-8"))
        timeNow = datetime.datetime.now().isoformat()
        timeNow = timeNow.split("T")
        timeNow = timeNow[0] + "@" + timeNow[1].split(".")[0]
        #self.message("602 Stats Bot joined "+self.channel+" on "+timeNow)
        #print("[Twitch IRC] "+ "Joined Twitch channel "+self.channel+".")
    def pong(self):
        try:
            self.currentSocket.send(bytes("PONG tmi.twitch.tv\r\n", "UTF-8"))
            timeNow = datetime.datetime.now().isoformat()
            timeNow = timeNow.split("T")
            timeNow = timeNow[0] + "@" + timeNow[1].split(".")[0]
            print("[Twitch] "+ timeNow +": Pong attempted.")
        except socket.error:
            print("[Twitch IRC] Socket error when attempting pong.")
