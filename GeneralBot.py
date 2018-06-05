import discord
import cv2
import requests
import shutil
import os
import random
import glob
import subprocess


class GeneralBot:
    def __init__(self, in_bot):
        self.bot = in_bot

    async def pepe(self, ctx, *args):
        await self.bot.send_file(ctx.message.channel, random.choice(glob.glob("/home/pi/Documents/glaelbot/pepes/*")))

    async def eyebleach(self, ctx, *args):
        await self.bot.send_file(ctx.message.channel, random.choice(glob.glob("/home/pi/Documents/glaelbot/eyebleach/*")))

    async def smug(self, ctx, *args):
        await self.bot.send_file(ctx.message.channel, random.choice(glob.glob("/home/pi/Documents/glaelbot/smug/*")))

    async def reverse(self, ctx, *args):
        result = ""
        for i in range(len(args)):
            result += args[i] + " "
        await self.bot.say(result[::-1])

    async def fortune(self, ctx, *args):
        if len(args)>0 and args[0] == "-o":
            string = subprocess.run(["/usr/games/fortune -o -n 300 -s"], stdout=subprocess.PIPE, shell=True).stdout
        else:
            string = subprocess.run(["/usr/games/fortune -n 300 -s"], stdout=subprocess.PIPE, shell=True).stdout
        await self.bot.say(string.decode())

    async def eightBall(self, ctx, *args):
        options = ["It is certain", "It is decidedly so", "Without a doubt", "Yes definitely", "You may rely on it", "As i see it, yes", "Most likely", "Outlook good", "Yes", "Signs point to yes", "Reply hazy try later", "Ask again later", "Better not tell you now", "Cannot predict now", "Concentrate and ask again", "Don't count on it", "My reply is no", "My sources say no", "Outlook not so good", "Very doubtful"]
        await self.bot.say(options[random.randint(0, 24)])

    async def star(self, ctx, *args):
        if len(args) > 0:
            if len(args[0]) <= 12:
                result = "```"
                word = args[0]
                for i in range(len(word) - 1):
                    result += " " * (i * 2)
                    result += word[len(word) - i - 1]
                    result += " " * ((len(word) - i) * 2 - 3)
                    result += word[len(word) - i - 1]
                    result += " " * ((len(word) - i) * 2 - 3)
                    result += word[len(word) - i - 1]
                    result += "\n"

                for i in range(len(word)):
                    result += word[len(word) - 1 - i]
                    result += " "
                for i in range(len(word) - 1):
                    result += word[i + 1]
                    result += " "
                result += "\n"

                for i in range(len(word) - 1):
                    result += " " * ((len(word) - 2 - i) * 2)
                    result += word[i + 1]
                    result += " " * ((i) * 2 + 1)
                    result += word[i + 1]
                    result += " " * ((i) * 2 + 1)
                    result += word[i + 1]
                    result += "\n"
            else:
                result = "```too long (╯°□°）╯︵ ┻━┻"
            result += "```"
            return await self.bot.say(result)
        else:
            return await self.bot.say("``` ```")

    async def echo(self, ctx, *args):
        if len(args) > 0:
            i = ""
            for a in range(len(args)):
                i += args[a]
                i += " "
            return await self.bot.say(i)
        else:
            return await self.bot.say("ECHO Echo echo ech...")

    async def add_reaction(self, message, reaction_string, server_string):
        emoji = self.bot.get_all_emojis()
        while True:
            a = next(emoji)
            if a.name == reaction_string and a.server.id == server_string:
                break
        await self.bot.add_reaction(message, a)

    async def ifunny_test(self, message):
        method = cv2.TM_SQDIFF_NORMED
        small_image = cv2.imread('/home/pi/Documents/glaelbot/watermark.png')
        url = message.attachments[0]["url"]
        response = requests.get(url, stream=True)
        name = url[-5:]
        with open(name, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response

        large_image = cv2.imread(name)

        result = cv2.matchTemplate(small_image, large_image, method)

        mn, B, mnLoc, A = cv2.minMaxLoc(result)
        os.remove(name)
        if mn <= 0.4:
            await self.bot.send_file(message.channel, "/home/pi/Documents/glaelbot/memePolice.jpg")
