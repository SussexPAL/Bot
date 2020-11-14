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


class PALbot(discord.Client):
    async def on_ready(self, banned=["@PAL"]):
        print("Logged on as", self.user)
        self.change_status.start()
        self.dataStruct = {}
        self.questions = 0
        self.banned = banned

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:  # do not reply to self
            return
        # log question
        Pass = False
        role = ""
        try:
            role = message.author.roles[0].name  # gather the role of the user
        except AttributeError:  # if DM
            Pass = True
        if role not in self.banned or Pass:  # don't anser these people
            info = [message.channel, ""]  # store channel from and messages
            if message.author.name not in self.dataStruct:
                self.questions += 1  # increase message count for admin
            arr = (
                self.dataStruct.get(message.author.name, info)[1]
                + " "
                + message.content.replace(":::", "/:").replace("@@@", "/@")
            )
            # add all messages from that user
            self.dataStruct[message.author.name] = [info[0], arr]

    @tasks.loop(seconds=60 * 60 * 24)  # every day email
    async def change_status(self):  # Notifications
        print(
            "email: There are ", self.questions, "Currently unanswered"
        )  # chage to email

    async def messageChat(self, message, c):  # message discord with given channel
        await c.send(message)


client = PALbot()


async def PALmentor(websocket, path):
    # Admin control loop
    # Called when admin connects to the server
    print("admin")
    try:
        async for message in websocket:
            # message structure: COMMAND:DataItem1:::DataItem2:::,....,:::DataItemN
            print(message)
            if message[0:7] == "ANSWER:":  # if answer code
                message = message.replace("ANSWER:", "")  # remove from string
                message = message.split(":::")  # split at given identifier
                # gather all information about the question
                name = message[0]
                question = client.dataStruct[name][1]
                c = client.dataStruct[name][0]
                client.dataStruct.pop(name)  # remove from data
                client.questions -= 1  # decrease value
                answer = message[1]
                await client.messageChat(
                    "@" + name + "\n '" + question + "' \n\n" + answer, c
                )
            elif message == "CONNECT":
                string = ""
                for i in client.dataStruct:
                    string += i + "@@@" + client.dataStruct[i][1] + ":::"
                    if len(string) > 500:  # prevent websocket error
                        break
                await websocket.send(string[:-3])  # send list of to add
            elif message[0:7] == "DELETE:":
                message = message.replace("DELETE:", "")  # remove from string
                client.dataStruct.pop(message)  # remove from data
    except websockets.exceptions.ConnectionClosedError:
        print("Admin left")


# Run the PAL server side
asyncio.get_event_loop().run_until_complete(
    websockets.serve(PALmentor, port=4040)
)  # listen for pal mentors

# Run the discord bot
client.run("T")
