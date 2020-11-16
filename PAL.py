"""
PAL bot code
Written by Dexter Shepherd, aged 19
Code runs and takes in questions from students
It also awaits requests from the web from pal mentors, allowing them to answer questions. 
"""

import discord
from discord.ext import commands, tasks
import asyncio
import websockets
import datetime

class Person:
    #class binding each person
    def __init__(self,name,channel):
        self.time=datetime.datetime.now()
        self.name=name
        self.channel=channel
        self.message=""
    def setMessage(self,message):
        self.message+=message

class PALbot(discord.Client):
    #the main bot
    #Stores unanswered questions
    #Removes when answered in chat by PAL mentor
    #Alerts PAL mentors to answer questions
    async def on_ready(self,banned=["@CEO"]):
        print('Logged on as', self.user)
        self.questions=0
        self.change_status.start()
        self.check_calendar.start()
        self.dataStruct={}
        self.banned=banned
        self.getQuestion="testing-site"
        #bot-testing
        self.setAnswer="testing-site"
        self.channels={}
        for i in self.get_all_channels():
                self.channels[str(i)]=i
    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user: #do not reply to self
            return
        #log question
        Pass=True
        roles=[]
        try:
            roles=message.author.roles #gather the role of the user
            for i in roles:
                if str(i.name) in self.banned: #don't answer these people
                    Pass=False
        except AttributeError: #if DM
            pass
        if str(message.channel) == self.getQuestion and (Pass): #if message in accepted channels from accepted people
            chan=self.channels[self.setAnswer]
            info=[chan,""] #store channel from and messages
            potentialPerson=Person(message.author.name,chan)
            message.content.replace(":::","/:").replace("@@@","/@")
            if message.author.name not in self.dataStruct:
                self.questions+=1 #increase message count for admin
            person=self.dataStruct.get(message.author.name,[potentialPerson])[0]
            person.setMessage(" "+message.content.replace(":::","/:").replace("@@@","/@"))
            #add all messages from that user
            self.dataStruct[message.author.name]=[person]
            
        elif not Pass or str(message.channel) == self.setAnswer:
            #check if this is a pal mentor answering a question
            check=message.mentions #get all mentioned in the message
            for i in check:
                if i.name in self.dataStruct: #if person has asked question
                    self.dataStruct.pop(i.name) #remove from data
    @tasks.loop(seconds=60*60) #every hour check what is happening
    async def check_calendar(self): #Notifications
        pass
    @tasks.loop(seconds=60*60*24) #every day check and message  
    async def change_status(self): #Notifications
        if self.questions>0:
            for i in self.dataStruct: #loop through each un-answered item
                t1=self.dataStruct[i][0].time #find the time it was sent
                nowTime=datetime.datetime.now() #get the current time
                timeSince=nowTime-t1
                timeSince=int(timeSince.total_seconds())/60/60 #get in hours
                if int(timeSince)>=24: #if sent more than 24 hours ago
                    await self.messageChat("@PAL The following questions need answering ASAP: \n\n"+"@"+i+" "+self.dataStruct[i][0].message+"\n\n",self.channels[self.setAnswer])
    async def messageChat(self,message,c): #message discord with given channel
        await c.send(message)
client=PALbot()

async def PALmentor(websocket, path):
    #Admin control loop
    #Called when admin connects to the server
    print("admin")
    try:
        async for message in websocket:
            #message structure: COMMAND:DataItem1:::DataItem2:::,....,:::DataItemN
            print(message)
            if message[0:7] == "ANSWER:": #if answer code
                message=message.replace("ANSWER:","") #remove from string
                message=message.split(":::") #split at given identifier
                #gather all information about the question
                name=message[0]
                person= client.dataStruct[name][0]
                question=person.message
                c=person.channel
                client.dataStruct.pop(name) #remove from data
                client.questions-=1 #decrease value
                answer=message[1]
                await client.messageChat("@"+name+"\n '"+question+"' \n\n"+answer,c)
            elif message=="CONNECT":
                string=""
                for i in client.dataStruct:
                    string+=i+"@@@"+client.dataStruct[i][0].message+":::"
                    if len(string)>500: #prevent websocket error
                        break
                await websocket.send(string[:-3]) #send list of to add
            elif message[0:7]=="DELETE:":
                message=message.replace("DELETE:","") #remove from string
                client.dataStruct.pop(message) #remove from data
    except websockets.exceptions.ConnectionClosedError:
            print("Admin left")
    
#Run the PAL server side
asyncio.get_event_loop().run_until_complete(
websockets.serve(PALmentor, port=4040)) #listen for pal mentors


#Run the discord bot
client.run(Test)
