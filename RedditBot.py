import discord
import random
import praw

class RedditBot:
    def __init__(self, in_bot, in_economy_bot):
        self.bot = in_bot
        self.economy_bot = in_economy_bot
        self.this_title_is_theonion = {}
        pwdFile = open("/home/glael/glaelbot/redditPwd.txt")
        redditPwd = pwdFile.read(8)
        self.reddit = praw.Reddit(client_id='19_lMJwVz3VNeg', client_secret='boVVSk__nNPPdmRqiuCGtbleuIY', username='MCglael', password=redditPwd, user_agent='test_script by glael')

    async def user_reacted(self, reaction, user):
        correctAnswer = self.this_title_is_theonion[reaction.message.embeds[0]["description"]]
        title = reaction.message.embeds[0]["description"]
        channel = reaction.message.channel
        await self.bot.delete_message(reaction.message)

        if str(reaction.emoji) == "🅰":
            if correctAnswer:
                await self.bot.send_message(channel, "Correct! This article was created by The Onion. You got 20bj$.\n" + '`' + title + '`')
                if (self.economy_bot.economy_manager.get_balance_of_player(user.id) >= 20):
                    self.economy_bot.economy_manager.increase_balance_of_player(user.id, 20, user.name)
                else:
                    await self.bot.send_message(channel, "Sadly, you did not have money, so you did not actually win money")
            else:
                await self.bot.send_message(channel, "Wrong! This article was NOT created by The Onion. You lost 20bj$.\n" + '`' + title + '`')
                if (self.economy_bot.economy_manager.get_balance_of_player(user.id) >= 20):
                    self.economy_bot.economy_manager.increase_balance_of_player(user.id, -20, user.name)
                else:
                    await self.bot.send_message(channel, "Luckily, you did not have money, so you did not actually lose money")
        elif str(reaction.emoji) == "🅱":
            if correctAnswer:
                await self.bot.send_message(channel, "Wrong! This article WAS created by The Onion. You lost 20bj$.\n" + '`' + title + '`')
                if (self.economy_bot.economy_manager.get_balance_of_player(user.id) >= 20):
                    self.economy_bot.economy_manager.increase_balance_of_player(user.id, -20, user.name)
                else:
                    await self.bot.send_message(channel, "Luckily, you did not have money, so you did not actually lose money")
            else:
                await self.bot.send_message(channel, "Correct! This article was not created by The Onion. You got 20bj$.\n" + '`' + title + '`')
                if (self.economy_bot.economy_manager.get_balance_of_player(user.id) >= 20):
                    self.economy_bot.economy_manager.increase_balance_of_player(user.id, 20, user.name)
                else:
                    await self.bot.send_message(channel, "Sadly, you did not have money, so you did not actually win money")




    async def notTheOnion(self, ctx, *args):
        loadingMsg = await self.bot.send_message(ctx.message.channel, "Loading...")

        new_embed = discord.Embed()
        new_embed.title = "/r/(not)TheOnion?"
        new_embed.colour = 0xDEADBF

        title = ""

        rand = random.randint(0,1)

        if rand == 1:
            theOnion = self.reddit.subreddit('theonion')

            pos = random.randint(0,100)

            iter = theOnion.hot(limit=100)

            for i in range(pos+1):
                title = iter.next()

            self.this_title_is_theonion[title.title] = 1

        else:
            notTheOnion = self.reddit.subreddit('nottheonion')

            pos = random.randint(0,100)

            iter = notTheOnion.hot(limit=100)

            for i in range(pos+1):
                title = iter.next()
            self.this_title_is_theonion[title.title] = 0

        new_embed.description = title.title
        new_embed.set_footer(text = 'react with 🅰 for /r/theOnion/, or with 🅱 for /r/notTheOnion/.')
        await self.bot.delete_message(loadingMsg)
        newmsg = await self.bot.send_message(ctx.message.channel, content="", embed=new_embed)

        await self.bot.add_reaction(newmsg, "🅰")
        await self.bot.add_reaction(newmsg, "🅱")
