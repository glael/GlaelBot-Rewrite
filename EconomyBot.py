import random
from BjEconomyManager import BjEconomyManager
import datetime
import discord
import asyncio
import threading
import gc
import blackjack as bj


class EconomyBot:
    def __init__(self, in_bot):
        self.economy_manager = BjEconomyManager()
        self.bot = in_bot
        self.blackjack_items = {}
        self.thread = threading.Timer(60.0, self.my_bj_timer)

    async def set_economy(self, ctx, *args):
        if ctx.message.author.id == "209305298769281024":
            self.economy_manager.set_balance_of_player(args[0], int(args[1]), args[2])

    async def economy(self, ctx, *args):
        self.economy_manager.read_economy()
        sender_id = ctx.message.author.id
        sender_name = ctx.message.author.name

        last_time = self.economy_manager.get_last_time_economy_received(sender_id)
        curr_time = datetime.datetime.now()

        message = ""
        if not self.economy_manager.exists(sender_id):
            self.economy_manager.increase_balance_of_player(sender_id, 50, sender_name)
            self.economy_manager.reset_last_time_economy_received(sender_id, sender_name)
            message += "Hi! For your first visit, you receive 50 bj$. Enter this same command again in 24h or more to receive more bj$.\n "
        elif last_time + datetime.timedelta(hours=24) >= curr_time:
            message += "You already have your bj$ for today. Try again later (after "
            message += (last_time + datetime.timedelta(hours=0)).strftime("%H:%M") + ").\n"
        else:
            self.economy_manager.increase_balance_of_player(sender_id, 100, sender_name)
            self.economy_manager.reset_last_time_economy_received(sender_id, sender_name)
            message += "You received 100 bj$. Return tomorrow for more!\n"
        message += "You currently have " + str(self.economy_manager.get_balance_of_player(sender_id)) + " bj$."
        await self.bot.send_message(ctx.message.channel, message)
        print("message sent")
        rank = open('/home/glael/glaelbot/rankings.txt', 'w')
        rank.write(self.economy_manager.get_list_of_balances())

    async def bjrank(self, ctx, *args):
        await self.bot.send_message(ctx.message.channel, self.economy_manager.get_list_of_balances())

    async def bjdice_get_amount(self, sender_name, sender_balance, amount_string, channel) -> int:
        if sender_balance < 1:
            await self.bot.send_message(channel, "You (" + sender_name + ") don't have any money.\n")
            return 0
        try:
            amount = int(amount_string)
            if sender_balance < abs(amount):
                await self.bot.say("You (" + sender_name + ") don't have enough money.\n")
                return 0
            return amount
        except ValueError:
            await self.bot.send_message("You (" + sender_name + ") didn't bet any money. Use `bjdice <number>` to bet money.\n")
            return 0
        except IndexError:
            await self.bot.send_message("You (" + sender_name + ") didn't bet any money. Use `bjdice <number>` to bet money.\n")
            return 0

    async def bjdice(self, ctx, *args):
        sender_id = ctx.message.author.id
        sender_name = ctx.message.author.name
        ec = self.economy_manager
        sender_balance = ec.get_balance_of_player(sender_id)
        amount = await self.bjdice_get_amount(sender_name, sender_balance, args[0], ctx.message.channel)

        bot_roll = random.randint(1, 6)
        player_roll = random.randint(1, 6)

        if bot_roll == player_roll:
            await self.bot.say("We both rolled " + str(
                bot_roll) + ". You (" + ctx.message.author.name + ") win nothing.")
        elif bot_roll > player_roll:
            await self.bot.say("You rolled " + str(player_roll) + ", and I rolled " + str(bot_roll) + ". You (" + ctx.message.author.name + ") lose " + str(amount) + " bj dollars.")
            ec.increase_balance_of_player(sender_id, -amount, sender_name)
        elif bot_roll < player_roll:
            await self.bot.say("You rolled " + str(player_roll) + ", and I rolled " + str(bot_roll) + ". You (" + ctx.message.author.name + ") win " + str(amount) + " bj dollars.")
            ec.increase_balance_of_player(sender_id, amount, sender_name)
        rank = open('/home/pi/Documents/glaelbot/rankings.txt', 'w')
        rank.write(self.economy_manager.get_list_of_balances())

    async def coin_drop(self, player_id, player_name, timestamp, channel):
        difference = datetime.datetime.utcnow() - timestamp
        await self.bot.send_message(channel, "Coin drop claimed after " + (datetime.datetime.utcfromtimestamp(0) + difference).strftime('%H:%M:%S') + " by " + player_name + ".")
        self.economy_manager.increase_balance_of_player(player_id, 50, player_name)

    async def reaction_added(self, reaction, user):
        with threading.RLock():
            react = self.convert_emoji_to_text(reaction.emoji)
            try:
                game = self.blackjack_items[reaction.message.channel.id]
                gamereacts = game.get_reactions()
                if react != "r" and react in gamereacts:
                    game.received_input(react, user.name)
                    await self.bot.remove_reaction(reaction.message, reaction.emoji, user)
                    await self.bot.edit_message(reaction.message, "d-d-d-duel!", embed=game.build_embed())
                    reacts = game.get_reactions()
                    for i in reacts:
                        await self.bot.add_reaction(reaction.message, self.convert_text_to_emoji(i))
                elif react == "r" and react in gamereacts:
                    del game
                    del self.blackjack_items[reaction.message.channel.id]
                    await self.bot.delete_message(reaction.message)
            except KeyError:
                await self.bot.send_message(reaction.message.channel, content="Woops, looks like that game is gone!")

    async def blackj(self, ctx, *args):
        if len(args) == 1:
            await self.blackjack_instantiate(ctx, args)
        elif len(args) == 2 and args[0].lower() == "and" and args[1].lower() == "hookers":
            await self.bot.send_message(ctx.message.channel, "And bring cocaïne!")
        elif len(args) == 0:
            await self.bot.send_message(ctx.message.channel, "You need to enter the amount of money you want to spend!")
        else:
            await self.bot.send_message(ctx.message.channel, ":angry:")

    async def blackjack_instantiate(self, ctx, *args):
        try:
            bet_amount = int(args[0][0])
        except ValueError:
            await self.bot.send_message(ctx.message.channel, "that's not a number")
            return

        if self.economy_manager.get_balance_of_player(ctx.message.author.id) >= bet_amount > 0:

            try:
                temp = self.blackjack_items[ctx.message.channel.id]
            except KeyError:
                self.blackjack_items[ctx.message.channel.id] = bj.BlackJack(self.economy_manager)
                if not self.thread.is_alive():
                    self.thread.start()
                message = await self.bot.send_message(ctx.message.channel, "starting")
                mess2 = (self.blackjack_items[ctx.message.channel.id]).start()
                embed = discord.Embed()
                embed.title = "BlackJack"
                await self.bot.edit_message(message, new_content=mess2, embed=embed)
                await self.bot.add_reaction(message, "🇽")
            finally:
                message = (self.blackjack_items[ctx.message.channel.id]).addPlayer(ctx.message.author, int(args[0][0]))
                mess = await self.bot.send_message(ctx.message.channel, message)
                await asyncio.sleep(1)
                await self.bot.delete_message(mess)
                # item = blackjackItems[ctx.message.channel.id]
                # await my_bot.edit_message(item.message, embed=item.build_embed())
                await self.bot.delete_message(ctx.message)
        else:
            await self.bot.send_message(ctx.message.channel, "you don't have enough moulah :angry:")

    def my_bj_timer(self):
        self.thread = threading.Timer(60.0, self.my_bj_timer)
        with threading.RLock():
            keys = self.blackjack_items.keys()
            for i in keys:
                self.blackjack_items[i].MinutesUntilDelete -= 1
            items_to_delete = [v for k, v in self.blackjack_items.items() if v.MinutesUntilDelete == 0]
            self.blackjack_items = {k: v for k, v in self.blackjack_items.items() if v.MinutesUntilDelete != 0}
            for i in items_to_delete:
                del i
            gc.collect()
        if len(self.blackjack_items) != 0:
            self.thread.start()

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

    def convert_text_to_emoji(self, text):
        emojiDict = {
            "a": "🇦",
            "b": "🇧",
            "c": "🇨",
            "d": "🇩",
            "e": "🇪",
            "f": "🇫",
            "g": "🇬",
            "h": "🇭",
            "i": "🇮",
            "j": "🇯",
            "k": "🇰",
            "l": "🇱",
            "m": "🇲",
            "n": "🇳",
            "o": "🇴",
            "p": "🇵",
            "q": "🇶",
            "r": "🇷",
            "s": "🇸",
            "t": "🇹",
            "u": "🇺",
            "v": "🇻",
            "w": "🇼",
            "x": "🇽",
            "y": "🇾",
            "z": "🇿"
        }
        output = ""
        for i in text:
            output += emojiDict[i]
        return output
