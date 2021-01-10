import datetime
import json
import traceback
import users
import settings
import time

def fetchIRC(thisChat, playerLookup):
    while True:
        try:
            readbuffer = thisChat.currentSocket.recv(4096).decode("UTF-8", errors = "ignore")
            if readbuffer == "": #reconnect on server disconnect
                print(datetime.datetime.now().isoformat().split(".")[0], "Empty readbuffer so reconnect:", thisChat.channel)
                thisChat.reconnect()
            lines = readbuffer.split("\n")
            for line in lines:
                process_line(line, thisChat, playerLookup)
        except ConnectionResetError:
            print(datetime.datetime.now().isoformat().split(".")[0], "ConnectionResetError:", thisChat.channel)
            thisChat.reconnect()
        except TimeoutError:
            print(datetime.datetime.now().isoformat().split(".")[0], "TimeoutError:", thisChat.channel)
            thisChat.reconnect()
        except Exception:
            print(datetime.datetime.now().isoformat().split(".")[0], "Unexpected error in", thisChat.channel)
            print(traceback.format_exc())
            time.sleep(1)
            thisChat.reconnect()

def process_line(line, currentChat, playerLookup):
    if line == "":
        return
    #print(line)
    line = line.rstrip().split()
    if len(line) == 0:
        return
    
    user = ""
    ismod = False
    userId = -1
    if line[0][0] == "@":
        tags = line.pop(0)
        tmp8 = tags.split("mod=")
        if len(tmp8) > 1:
            if tmp8[1][0] == "1":
                ismod = True
        tmp9 = tags.split("user-id=")
        if len(tmp9) > 1:
            userId = tmp9[1].split(";")[0]
    
    with open(f"irc/{currentChat.channel}.log", 'a') as f:
        f.write(datetime.datetime.now().isoformat().split(".")[0] + " " + " ".join(line) + "\n")

    command = []
    for index, word in enumerate(line):
        if index == 0:
            user = word.split('!')[0]
            #user = user[0:24] # what's this for?
            if user == "PING":
                currentChat.pong()
                return
            # if user.__contains__("."):
            #     return
            if len(line) < 4:
                return
        if index == 3:
            if len(word) <= 1:
                return
            command.append(word.lower()[1:])
        if index >= 4:
            command.append(word)
    
    
    #print("[user]", user, "[command]", command, "[userid]", userid, "[ismod]", ismod)
    
    if command[0] not in ['!ping','!roles','!racecommands','!whitelist','!unwhitelist','!add','!set','!rejoin','!quit','!start','!forcequit','!dq','!noshow', '!revive', '!settime', '!blacklist', '!unblacklist', '!admin', '!debugquit']:
        return
    user = user.lower()[1:]
    print("[In chat "+currentChat.channel+"] "+user+":"+str(command))

    # global commands
    if command[0] == "!ping":
        currentChat.message("Hi. Bot is alive.")
    if command[0] == "!racecommands":
        currentChat.message("Command list: https://pastebin.com/d7mPZd13")
    if command[0] == "!roles":
        if len(command) == 1:
            statusMsg = users.status(user, playerLookup)
        else:
            statusMsg = users.status(command[1], playerLookup)
        if statusMsg is not None:
            currentChat.message(statusMsg)

    # shared commands
    if (user in users.admins) or (user in users.racersL):
        if command[0] == "!whitelist" and len(command) == 2:
            if command[1] in users.blacklist:
                currentChat.message("Sorry, " + command[1] + " is on the blacklist.")
            elif command[1] not in users.updaters:
                users.add(command[1],users.Role.UPDATER)
                currentChat.message(command[1] + " is now an updater.")
            else:
                currentChat.message(command[1] + " is already an updater.")
        elif command[0] == "!unwhitelist" and len(command) == 2:
            if command[1] in users.updaters:
                users.remove(command[1],users.Role.UPDATER)
                currentChat.message(command[1] + " is no longer an updater.")
            else:
                currentChat.message(command[1] + " is already not an updater.")

    # racer commands
    if user in users.racersL:
        if (command[0] == "!add" or command[0] == "!set") and len(command) == 2:
            try:
                number = int(command[1])
                if user in playerLookup.keys():
                    response = ""
                    if command[0] == "!add":
                        response = playerLookup[user].update(playerLookup[user].collects + number)
                    elif command[0] == "!set":
                        response = playerLookup[user].update(number)
                    if response != "":
                        currentChat.message(response)
                    settings.redraw = True
            except ValueError:
                pass
        
        if (command[0] == "!rejoin"):
            if playerLookup[user].status == "quit":
                playerLookup[user].status = "live"
                currentChat.message(playerLookup[user].nameCaseSensitive +" has rejoined the race.")
            elif playerLookup[user].status == "done":
                playerLookup[user].collects -= 1
                playerLookup[user].status = "live"
                currentChat.message(playerLookup[user].nameCaseSensitive +" has rejoined the race.")
            settings.redraw = True
        
        if command[0] == "!quit" and playerLookup[user].status == "live":
            playerLookup[user].fail("quit", settings.startTime)
            settings.redraw = True
            currentChat.message(playerLookup[user].nameCaseSensitive + " has quit.")

    # updater commands
    if ((user in users.updaters) or (ismod==True) or (user in users.racersL)) and (user not in users.blacklist):
        if (command[0] == "!add" or command[0] == "!set") and len(command) == 3:
            player = command[1]
            try:
                number = int(command[2])
                if player in playerLookup.keys():
                    response = ""
                    if command[0] == "!add":
                        response = playerLookup[player].update(playerLookup[player].collects + number)
                    elif command[0] == "!set":
                        response = playerLookup[player].update(number)
                    if response != "":
                        currentChat.message(response)
                    settings.redraw = True
            except ValueError:
                pass

    # admin commands
    if user in users.admins:
        if command[0] == "!start":
            newTime = -1
            if len(command)==1:
                newTime = datetime.datetime.now()
            elif len(command)==2:
                newTime = command[1]
                try:
                    newTime = datetime.datetime.fromisoformat(newTime)
                except ValueError:
                    currentChat.message("Invalid date format. Must be of this format: 2018-12-29@09:00")
            else:
                currentChat.message("Invalid date format. Must be of this format: 2018-12-29@09:00")
            if type(newTime) == datetime.datetime:
                settings.startTime = newTime
                with open('settings.json', 'r+') as f:
                    j = json.load(f)
                    j['start-time'] = settings.startTime.isoformat().split(".")[0]
                    f.seek(0)
                    json.dump(j, f, indent=4)
                    f.truncate()
                currentChat.message("The race start time has been set to " + settings.startTime.isoformat().split(".")[0])
                for player in playerLookup.keys():
                    playerLookup[player].calculateCompletionTime(settings.startTime)
                settings.redraw = True
        elif command[0] == "!forcequit":
            if len(command) == 2 and command[1] in playerLookup.keys():
                player = command[1]
                if playerLookup[player].status == "live" or playerLookup[player].status == "done":
                    playerLookup[player].fail("quit", settings.startTime)
                    settings.redraw = True
                    currentChat.message(command[1] + " has been forcequit.")
        elif command[0] == "!noshow":
            if len(command) == 2 and command[1] in playerLookup.keys():
                player = command[1]
                playerLookup[player].fail("noshow", settings.startTime)
                settings.redraw = True
                currentChat.message(command[1] + " set to No-show.")
        elif command[0] == "!dq":
            if len(command) == 2 and command[1] in playerLookup.keys():
                player = command[1]
                if playerLookup[player].status == "live" or playerLookup[player].status == "done":
                    playerLookup[player].fail("disqualified", settings.startTime)
                    settings.redraw = True
                    currentChat.message(command[1] + " has been disqualified.")
        elif command[0] == "!revive":
            if len(command) == 2 and command[1] in playerLookup.keys():
                player = command[1]
                if playerLookup[player].status == "done":
                    playerLookup[player].collects -= 1
                playerLookup[player].status = "live"
                settings.redraw = True
                currentChat.message(command[1] + " has been revived.")
        elif command[0] == "!settime":
            if len(command) == 3 and command[1] in playerLookup.keys():
                player = playerLookup[command[1]]
                stringTime = command[2]
                newTime = command[2].split(":")
                if len(newTime) != 3:
                    currentChat.message("Invalid time string.")
                    return
                try:
                    duration = int(newTime[2]) + 60*int(newTime[1]) + 3600*int(newTime[0])
                except ValueError:
                    currentChat.message("Invalid time string.")
                    return
                if int(newTime[1]) >= 60 or int(newTime[2]) >= 60:
                    currentChat.message("Invalid time string.")
                    return
                
                player.duration = duration
                player.completionTime = stringTime
                player.manualDuration(settings.startTime)
                settings.redraw = True
                currentChat.message(player.nameCaseSensitive+"'s time has been updated.")
        elif command[0] == "!blacklist" and len(command) == 2:
            if command[1] not in users.blacklist:
                users.add(command[1],users.Role.BLACKLIST)
                if command[1] in users.updaters:
                    users.remove(command[1],users.Role.UPDATER)
                currentChat.message(command[1] + " has been blacklisted.")
            else:
                currentChat.message(command[1] + " is already blacklisted.")
        elif command[0] == "!unblacklist" and len(command) == 2:
            if command[1] in users.blacklist:
                users.remove(command[1],users.Role.BLACKLIST)
                currentChat.message(command[1] + " is no longer blacklisted.")
            else:
                currentChat.message(command[1] + " is already not blacklisted.")
        elif command[0] == "!admin" and len(command) == 2:
            if command[1] not in users.admins:
                users.add(command[1],users.Role.ADMIN)
                currentChat.message(command[1] + " is now an admin.")
            else:
                currentChat.message(command[1] + " is already an admin.")
        elif command[0] == "!debugquit":
            settings.doQuit = True