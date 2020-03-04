import discord
import random


class GalgjeBot:
    def __init__(self, in_bot):
        self.bot = in_bot
        self.current_galgje_word = {}

    async def galgje(self, ctx, *args):
        next_galgje_word = random.randint(0, 126917)

        galgje_embed = discord.Embed()
        galgje_embed.title = "Galgje"
        galgje_embed.colour = discord.Colour.blue()

        description = "`"
        f = open('/home/glael/glaelbot/groeneBoekje.txt')
        lines = f.readlines()
        for i in range(len(lines[next_galgje_word]) - 1):
            description += "_ "
        description += "`"
        galgje_embed.description = description + '\n\n\n(0/10)'

        sent_message = await self.bot.send_message(ctx.message.channel, embed=galgje_embed)
        self.current_galgje_word[sent_message.id] = next_galgje_word
        print(lines[next_galgje_word])

    async def user_reacted(self, reaction, user):
        new_embed = discord.Embed()
        new_embed.title = reaction.message.embeds[0]["title"]
        description = reaction.message.embeds[0]["description"]
        reacted_letter = self.convert_emoji_to_text(reaction.emoji)

        f = open('/home/glael/glaelbot/groeneBoekje.txt')
        lines = f.readlines()
        if reacted_letter.lower() not in lines[self.current_galgje_word[reaction.message.id]]:
            i = description.rfind("\n")
            description = description[:i] + reacted_letter.upper() + " " + description[i:]
            times_guessed_before = int(description[description.rfind("(") + 1:description.rfind("/")])
            description = description[:description.rfind("(") + 1] + str(times_guessed_before + 1) + description[description.rfind("/"):]
            if times_guessed_before + 1 == 10:
                description += " 🎉"
        else:
            for i in range(len(lines[self.current_galgje_word[reaction.message.id]])):
                if description[i * 2 + 1] == "_" and lines[self.current_galgje_word[reaction.message.id]][i] == reacted_letter:
                    description = description[:i * 2 + 1] + reacted_letter.upper() + description[i * 2 + 2:]

        if "_" not in description:
            description += "\nYOU WIN"
            del self.current_galgje_word[reaction.message.id]
        new_embed.description = description
        new_embed.colour = reaction.message.embeds[0]["color"]
        await self.bot.edit_message(reaction.message, embed=new_embed)
        await self.bot.remove_reaction(reaction.message, reaction.emoji, user)
        return

    def convert_emoji_to_text(self, emoji):
        emojiDict = {
            "🇦": "a",
            "🇧": "b",
            "🇨": "c",
            "🇩": "d",
            "🇪": "e",
            "🇫": "f",
            "🇬": "g",
            "🇭": "h",
            "🇮": "i",
            "🇯": "j",
            "🇰": "k",
            "🇱": "l",
            "🇲": "m",
            "🇳": "n",
            "🇴": "o",
            "🇵": "p",
            "🇶": "q",
            "🇷": "r",
            "🇸": "s",
            "🇹": "t",
            "🇺": "u",
            "🇻": "v",
            "🇼": "w",
            "🇽": "x",
            "🇾": "y",
            "🇿": "z"
        }
        output = ""
        for i in emoji:
            output += emojiDict[i]
        return output
