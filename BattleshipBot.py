import numpy
import time
import asyncio
import discord
import random


class BattleshipBot:
    def __init__(self, in_bot):
        self.bot = in_bot
        self.gameStatus = 0  # 0=noGame 1=setup 2=playing
        self.setupStatus = 0  # 0=coords 1=direction
        self.setupBoatsPlaced = 0
        self.setupLastPlace = [0, 0]
        self.BOARD_SIZE = 9
        self.AVAILABLE_BOAT_SIZES = [5, 4, 3, 3, 2]
        self.BOAT_NAMES = ["Carrier", "Battleship", "Cruiser", "Submarine", "Destroyer"]
        self.previousBotBoardMessage = 0
        self.previousPlayerBoardMessage = 0
        self.winner = 0  # 0 = Player, 1 = Bot
        self.playerBoard = numpy.zeros((self.BOARD_SIZE, self.BOARD_SIZE))  # 0=liveWater 1=deadWater 2=liveBoat 3=deadBoat 4=setupOnlyOne 5=notWholeBoatDead
        self.botBoard = numpy.zeros((self.BOARD_SIZE, self.BOARD_SIZE))
        self.emojiWater = ""
        self.emojiBoatEndL = ""
        self.emojiBoatEndR = ""
        self.emojiBoatEndU = ""
        self.emojiBoatEndD = ""
        self.emojiBoatMidH = ""
        self.emojiBoatMidV = ""
        self.emojiUnknown = ""
        self.hEmojiWater = ""
        self.hEmojiBoatEndL = ""
        self.hEmojiBoatEndR = ""
        self.hEmojiBoatEndU = ""
        self.hEmojiBoatEndD = ""
        self.hEmojiBoatMidH = ""
        self.hEmojiBoatMidV = ""
        self.hEmojiUnknown = ""

    async def startGameDefaultLayout(self, channel):
        self.playerBoard = numpy.zeros((self.BOARD_SIZE, self.BOARD_SIZE))
        self.playerBoard[1][0] = 2
        self.playerBoard[1][1] = 2
        self.playerBoard[1][2] = 2
        self.playerBoard[1][3] = 2
        self.playerBoard[1][4] = 2

        self.playerBoard[8][2] = 2
        self.playerBoard[8][3] = 2
        self.playerBoard[8][4] = 2
        self.playerBoard[8][5] = 2

        self.playerBoard[3][4] = 2
        self.playerBoard[4][4] = 2
        self.playerBoard[5][4] = 2

        self.playerBoard[6][7] = 2
        self.playerBoard[7][7] = 2
        self.playerBoard[8][7] = 2

        self.playerBoard[0][6] = 2
        self.playerBoard[1][6] = 2
        await self.startActualGame(channel)

    async def startActualGame(self, channel):
        self.gameStatus = 2
        await self.showBotBoard(channel)
        await self.showPlayerBoard(channel)

    async def evalReaction(self, reaction):
        if self.gameStatus == 1 and self.setupStatus == 1:
            if reaction.emoji == "🇳":
                if self.checkIfValidBoatPlacement(0, True):
                    self.placeBoat(0, True)
                    await self.askPlayerForBoatPlace(reaction.message.channel)
                else:
                    await self.cancelBoatPlacement(reaction.message.channel)
            elif reaction.emoji == "🇪":
                if self.checkIfValidBoatPlacement(1, True):
                    self.placeBoat(1, True)
                    await self.askPlayerForBoatPlace(reaction.message.channel)
                else:
                    await self.cancelBoatPlacement(reaction.message.channel)
            elif reaction.emoji == "🇸":
                if self.checkIfValidBoatPlacement(2, True):
                    self.placeBoat(2, True)
                    await self.askPlayerForBoatPlace(reaction.message.channel)
                else:
                    await self.cancelBoatPlacement(reaction.message.channel)
            elif reaction.emoji == "🇼":
                if self.checkIfValidBoatPlacement(3, True):
                    self.placeBoat(3, True)
                    await self.askPlayerForBoatPlace(reaction.message.channel)
                else:
                    await self.cancelBoatPlacement(reaction.message.channel)
            else:
                print("wrong emote")

    def placeBoat(self, direction, player):
        if direction == 0:
            direction1 = 0
            direction2 = -1
        elif direction == 1:
            direction1 = 1
            direction2 = 0
        elif direction == 3:
            direction1 = -1
            direction2 = 0
        else:
            direction1 = 0
            direction2 = 1
        for i in range(self.AVAILABLE_BOAT_SIZES[self.setupBoatsPlaced]):
            if player:
                self.playerBoard[self.setupLastPlace[0]+i*direction1][self.setupLastPlace[1]+i*direction2] = 2
            else:
                self.botBoard[self.setupLastPlace[0]+i*direction1][self.setupLastPlace[1]+i*direction2] = 2
        self.setupBoatsPlaced += 1
        self.setupStatus = 0

    async def cancelBoatPlacement(self, channel):
        self.playerBoard[self.setupLastPlace[0]][self.setupLastPlace[1]] = 0
        self.setupStatus = 0
        await self.bot.send_message(channel, "That is not a valid direction (boats may not touch each other, except diagonally).")
        await self.showPlayerBoard(channel)

    async def evalMessage(self, message):
        if self.gameStatus == 1 and self.setupStatus == 0 and message.content == "DefLay":
            await self.startGameDefaultLayout(message.channel)
            return
        if (message.content[0] not in "ABCDEFGHI") or (message.content[1] not in "123456789"):
            return
        if self.gameStatus == 0:
            return
        elif self.gameStatus == 1 and self.setupStatus == 0 and len(message.content) == 2:
            await self.evalPlaceShip(message)
        elif self.gameStatus == 2 and len(message.content) == 2:
            await self.evalShootOpponent(message)
        return

    async def evalShootOpponent(self, message):
        Let = "ABCDEFGHI".find(message.content[0])
        Num = int(message.content[1]) - 1

        if self.botBoard[Num][Let] == 0:
            self.botBoard[Num][Let] = 1
            await self.botShoot(message)
        elif self.botBoard[Num][Let] == 2:
            self.botBoard[Num][Let] = 5
            await self.checkIfBoatIsComplete(Num, Let, True)
            await self.botShoot(message)
        elif self.botBoard[Num][Let] == 1 or self.botBoard[Num][Let] == 3 or self.botBoard[Num][Let] == 5:
            await self.bot.send_message(message.channel, "You already hit those coordinates. Try again.")
        await self.showBotBoard(message.channel)
        await self.showPlayerBoard(message.channel)

    async def botShoot(self, message):
        x = random.randint(0, self.BOARD_SIZE - 1)
        y = random.randint(0, self.BOARD_SIZE - 1)

        for i in range(self.BOARD_SIZE):
            for j in range(self.BOARD_SIZE):
                if self.playerBoard[i][j] == 5:
                    if (i-1 >=0 and j >= 0 and i-1 < self.BOARD_SIZE and j < self.BOARD_SIZE) and self.getValueAtBoardPosition(i-1, j, True) in [2, 0]:
                        if self.getValueAtBoardPosition(i-1, j, True) == 2:
                            self.playerBoard[i-1, j] = 5
                            await self.bot.send_message(message.channel, "Bot shot at " + chr(j + 65) + str(i - 1 + 1) + " and hit your boat.")
                            await self.checkIfBoatIsComplete(i, j, False)
                            return
                        else:
                            self.playerBoard[i-1, j] = 1
                            await self.bot.send_message(message.channel, "Bot shot at " + chr(j + 65) + str(i - 1 + 1) + " and missed.")
                            return
                    if (i+1 >= 0 and j >= 0 and i+1 < self.BOARD_SIZE and j < self.BOARD_SIZE) and self.getValueAtBoardPosition(i+1, j, True) in [2, 0]:
                        if self.getValueAtBoardPosition(i+1, j, True) == 2:
                            self.playerBoard[i+1, j] = 5
                            await self.bot.send_message(message.channel, "Bot shot at " + chr(j + 65) + str(i + 1 + 1) + " and hit your boat.")
                            await self.checkIfBoatIsComplete(i, j, False)
                            return
                        else:
                            self.playerBoard[i+1, j] = 1
                            await self.bot.send_message(message.channel, "Bot shot at " + chr(j + 65) + str(i + 1 + 1) + " and missed.")
                            return
                    if (i >= 0 and j-1 >= 0 and i < self.BOARD_SIZE and j-1 < self.BOARD_SIZE) and self.getValueAtBoardPosition(i, j-1, True) in [2, 0]:
                        if self.getValueAtBoardPosition(i, j-1, True) == 2:
                            self.playerBoard[i, j-1] = 5
                            await self.bot.send_message(message.channel, "Bot shot at " + chr(j - 1 + 65) + str(i + 1) + " and hit your boat.")
                            await self.checkIfBoatIsComplete(i, j, False)
                            return
                        else:
                            self.playerBoard[i, j-1] = 1
                            await self.bot.send_message(message.channel, "Bot shot at " + chr(j - 1 + 65) + str(i + 1) + " and missed.")
                            return
                    if (i >= 0 and j+1 >= 0 and i < self.BOARD_SIZE and j+1 < self.BOARD_SIZE) and self.getValueAtBoardPosition(i, j+1, True) in [2, 0]:
                        if self.getValueAtBoardPosition(i, j+1, True) == 2:
                            self.playerBoard[i, j+1] = 5
                            await self.bot.send_message(message.channel, "Bot shot at " + chr(j + 1 + 65) + str(i + 1) + " and hit your boat.")
                            await self.checkIfBoatIsComplete(i, j, False)
                            return
                        else:
                            self.playerBoard[i, j+1] = 1
                            await self.bot.send_message(message.channel, "Bot shot at " + chr(j + 1 + 65) + str(i + 1) + " and missed.")
                            return

        if self.playerBoard[x][y] == 0:
            self.playerBoard[x][y] = 1
            await self.bot.send_message(message.channel, "Bot shot at " + chr(y+65) + str(x+1) + " and missed.")
        elif self.playerBoard[x][y] == 2:
            self.playerBoard[x][y] = 5
            await self.bot.send_message(message.channel, "Bot shot at " + chr(y+65) + str(x+1) + " and hit your boat.")
            await self.checkIfBoatIsComplete(x, y, False)
        elif self.playerBoard[x][y] == 1 or self.playerBoard[x][y] == 3 or self.playerBoard[x][y] == 5:
            await self.botShoot(message)

    async def checkIfPlayerHasWon(self):
        for i in range(len(self.botBoard)):
            for j in range(len(self.botBoard[i])):
                if self.getValueAtBoardPosition(i, j, False) == 2:
                    return
        self.gameStatus = 0
        self.winner = 0
        print("player won")

    async def checkIfBotHasWon(self):
        for i in range(len(self.playerBoard)):
            for j in range(len(self.playerBoard[i])):
                if self.getValueAtBoardPosition(i, j, True) == 2:
                    return
        self.gameStatus = 0
        self.winner = 1
        print("bot won")

    async def resetBattleShip(self):
        self.playerBoard = numpy.zeros((self.BOARD_SIZE, self.BOARD_SIZE))
        self.botBoard = numpy.zeros((self.BOARD_SIZE, self.BOARD_SIZE))
        self.setupBoatsPlaced = 0
        self.gameStatus = 0
        self.setupStatus = 0

    async def checkIfBoatIsComplete(self, Num, Let, Player):
        if not self.checkIfFiveIsConnectedToTwo(Num, Let, Num, Let, Player):
            self.floodFillFiveToThree(Num, Let, Player)
            if Player:
                await self.checkIfPlayerHasWon()
            else:
                await self.checkIfBotHasWon()

    def checkIfFiveIsConnectedToTwo(self, Num, Let, prevNum, prevLet, Player):
        if self.getValueAtBoardPosition(Num-1, Let, not Player) == 2 or self.getValueAtBoardPosition(Num+1, Let, not Player) == 2 or self.getValueAtBoardPosition(Num, Let-1, not Player) == 2 or self.getValueAtBoardPosition(Num, Let+1, not Player) == 2:
            return True
        if self.getValueAtBoardPosition(Num-1, Let, not Player) == 5 and Num-1 != prevNum:
            if self.checkIfFiveIsConnectedToTwo(Num-1, Let, Num, Let, Player):
                return True
        if self.getValueAtBoardPosition(Num+1, Let, not Player) == 5 and Num+1 != prevNum:
            if self.checkIfFiveIsConnectedToTwo(Num+1, Let, Num, Let, Player):
                return True
        if self.getValueAtBoardPosition(Num, Let-1, not Player) == 5 and Let-1 != prevLet:
            if self.checkIfFiveIsConnectedToTwo(Num, Let-1, Num, Let, Player):
                return True
        if self.getValueAtBoardPosition(Num, Let+1, not Player) == 5 and Let+1 != prevLet:
            if self.checkIfFiveIsConnectedToTwo(Num, Let+1, Num, Let, Player):
                return True
        return False

    def floodFillFiveToThree(self, Num, Let, Player):

        a = self.getValueAtBoardPosition(Num-1, Let, not Player)
        b = self.getValueAtBoardPosition(Num+1, Let, not Player)
        c = self.getValueAtBoardPosition(Num, Let-1, not Player)
        d = self.getValueAtBoardPosition(Num, Let+1, not Player)

        if Player:
            self.botBoard[Num][Let] = 3
        else:
            self.playerBoard[Num][Let] = 3
        if self.getValueAtBoardPosition(Num-1, Let, not Player) == 5:
            self.floodFillFiveToThree(Num - 1, Let, Player)
        if self.getValueAtBoardPosition(Num+1, Let, not Player) == 5:
            self.floodFillFiveToThree(Num + 1, Let, Player)
        if self.getValueAtBoardPosition(Num, Let-1, not Player) == 5:
            self.floodFillFiveToThree(Num, Let - 1, Player)
        if self.getValueAtBoardPosition(Num, Let+1, not Player) == 5:
            self.floodFillFiveToThree(Num, Let + 1, Player)

    async def evalPlaceShip(self, message):
        Let = "ABCDEFGHI".find(message.content[0])
        Num = int(message.content[1]) - 1
        coords = [Num, Let]

        if not self.checkValidPlaceForBoat(coords, True):
            await self.bot.send_message(message.channel, "Those coordinates are not valid (boats may not touch each other, except diagonally).")
            return

        self.setupLastPlace = coords
        self.playerBoard[Num][Let] = 4
        self.setupStatus = 1

        try:
            if self.previousPlayerBoardMessage != 0:
                await self.bot.delete_message(self.previousPlayerBoardMessage)
        except discord.errors.NotFound:
            a = 1
        finally:
            boatLengthToPlace = self.AVAILABLE_BOAT_SIZES[self.setupBoatsPlaced]
            em = discord.Embed(title='Battleship: your waters.', description=self.generateBoardStringPlayer())

            hint = "In what direction do you want to place your " + self.BOAT_NAMES[self.setupBoatsPlaced]
            hint += " (length = " + str(boatLengthToPlace) + ")? React with the correct direction."

            em.add_field(name="Lay out your ships.", value=hint)
            if not self.gameStatus == 0:
                self.previousPlayerBoardMessage = sent_message = await self.bot.send_message(message.channel, embed=em)
            else:
                self.previousPlayerBoardMessage = 0
                sent_message = await self.bot.send_message(message.channel, embed=em)
            await self.bot.add_reaction(sent_message, "🇳")
            await self.bot.add_reaction(sent_message, "🇪")
            await self.bot.add_reaction(sent_message, "🇸")
            await self.bot.add_reaction(sent_message, "🇼")

    def checkValidPlaceForBoat(self, coords, player):
        if coords[0] < 0 or coords[1] < 0 or coords[0] >= self.BOARD_SIZE or coords[1] >= self.BOARD_SIZE:
            return False
        if self.getValueAtBoardPosition(coords[0]+1, coords[1], player) != 0:
            return False
        if self.getValueAtBoardPosition(coords[0]-1, coords[1], player) != 0:
            return False
        if self.getValueAtBoardPosition(coords[0], coords[1]+1, player) != 0:
            return False
        if self.getValueAtBoardPosition(coords[0], coords[1]-1, player) != 0:
            return False
        return True

    def checkIfValidBoatPlacement(self, direction, player):  # 0=North, 1=East, ...
        if direction == 0:
            direction1 = 0
            direction2 = -1
        elif direction == 1:
            direction1 = 1
            direction2 = 0
        elif direction == 3:
            direction1 = -1
            direction2 = 0
        else:
            direction1 = 0
            direction2 = 1
        if player:
            self.playerBoard[self.setupLastPlace[0]][self.setupLastPlace[1]] = 0
        else:
            self.botBoard[self.setupLastPlace[0]][self.setupLastPlace[1]] = 0
        for i in range(self.AVAILABLE_BOAT_SIZES[self.setupBoatsPlaced]):
            currentX = self.setupLastPlace[0]+direction1*i
            currentY = self.setupLastPlace[1]+direction2*i
            #print("checking " + str(currentX) + " " + str(currentY))
            if currentX < 0 or currentY < 0 or currentX >= self.BOARD_SIZE or currentY >= self.BOARD_SIZE:
                return False
            if self.getValueAtBoardPosition(currentX + 1, currentY, player) != 0:
                return False
            if self.getValueAtBoardPosition(currentX - 1, currentY, player) != 0:
                return False
            if self.getValueAtBoardPosition(currentX, currentY + 1, player) != 0:
                return False
            if self.getValueAtBoardPosition(currentX, currentY - 1, player) != 0:
                return False
        return True

    async def showPlayerBoard(self, channel):
        try:
            if self.previousPlayerBoardMessage != 0:
                await self.bot.delete_message(self.previousPlayerBoardMessage)
        except discord.errors.NotFound:
            a = 1
        finally:
            em = discord.Embed(title='Battleship: your waters.', description=self.generateBoardStringPlayer())
            if self.gameStatus == 0:
                self.playerBoard = numpy.zeros((self.BOARD_SIZE, self.BOARD_SIZE))
                self.botBoard = numpy.zeros((self.BOARD_SIZE, self.BOARD_SIZE))
                self.setupBoatsPlaced = 0
                if self.winner == 0:
                    message = "Congratulations! You won! https://youtu.be/1Bix44C1EzY"
                else:
                    message = "Oh no! You lost. Better luck next time. https://glael.s-ul.eu/OkbIvn6Q"
            else:
                message = ""
            if not self.gameStatus == 0:
                self.previousPlayerBoardMessage = await self.bot.send_message(channel, embed=em, content=message)
            else:
                self.previousPlayerBoardMessage = 0
                await self.bot.send_message(channel, embed=em, content=message)

    async def showBotBoard(self, channel):
        try:
            if self.previousBotBoardMessage != 0:
                await self.bot.delete_message(self.previousBotBoardMessage)
        except discord.errors.NotFound:
            a = 1
        finally:
            em = discord.Embed(title='Battleship: bot\'s waters.', description=self.generateBoardStringBot())
            if not self.gameStatus == 0:
                self.previousBotBoardMessage = await self.bot.send_message(channel, embed=em)
            else:
                self.previousBotBoardMessage = 0
                await self.bot.send_message(channel, embed=em)

    async def startNewGame(self, ctx, *args):
        if self.gameStatus != 0:
            await self.bot.say("A game is already in progress. Finish that first.")
            return
        self.gameStatus = 1
        self.generateBotBoardPositions()
        await self.askPlayerForBoatPlace(ctx.message.channel)

    async def askPlayerForBoatPlace(self, channel):
        try:
            if self.previousPlayerBoardMessage != 0:
                await self.bot.delete_message(self.previousPlayerBoardMessage)
        except discord.errors.NotFound:
            a = 1
        finally:
            if self.setupBoatsPlaced > 4:
                await self.startActualGame(channel)
                return
            boatLengthToPlace = self.AVAILABLE_BOAT_SIZES[self.setupBoatsPlaced]
            em = discord.Embed(title='Battleship: your waters.', description=self.generateBoardStringPlayer())

            hint = "Where do you want to place your " + self.BOAT_NAMES[self.setupBoatsPlaced]
            hint += " (length = " + str(boatLengthToPlace) + ")? Give coordinates of one end (for example: D3)."

            em.add_field(name="Lay out your ships.", value=hint)
            if not self.gameStatus == 0:
                self.previousPlayerBoardMessage = await self.bot.send_message(channel, embed=em)
            else:
                self.previousPlayerBoardMessage = 0
                await self.bot.send_message(channel, embed=em)

    def generateBotBoardPositions(self):
        i = -1
        while i < 4:
            i += 1
            #print("trying to place boat " + str(i))
            #print("self.setupBoatsPlaced: " + str(self.setupBoatsPlaced))
            randX = random.randint(0, self.BOARD_SIZE - 1)
            randY = random.randint(0, self.BOARD_SIZE - 1)
            randDir = random.randint(0, 3)
            #print("attempting to place at: " + str(randX) + " " + str(randY) + " , direction: " + str(randDir))

            if not self.checkValidPlaceForBoat([randX, randY], False):
                i -= 1
                #print("placeCheck failed")
                continue
            #print("placeCheck succeeded")
            self.setupLastPlace = [randX, randY]
            self.botBoard[randX][randY] = 4

            if not self.checkIfValidBoatPlacement(randDir, False):
                i -= 1
                self.botBoard[randX][randY] = 0
                #print("placementCheck failed")
                continue
            #print("placementCheck succeeded")
            self.placeBoat(randDir, False)
        self.setupBoatsPlaced = 0
        self.setupStatus = 0

    async def RevealAlBotBoats(self, ctx, *args):
        for i in range(self.BOARD_SIZE):
            for j in range(self.BOARD_SIZE):
                if self.botBoard[i][j] == 2:
                    self.botBoard[i][j] = 3
        self.gameStatus = 0
        self.winner = 0
        self.setupBoatsPlaced = 0
        await self.showBotBoard(ctx.message.channel)
        await self.showPlayerBoard(ctx.message.channel)

    def generateEmoji(self):
        emoji = self.bot.get_all_emojis()
        while True:
            try:
                e = next(emoji)
                if e.name == "aa" and e.server.id == "231823001912475648":
                    self.emojiWater = str(e)
                elif e.name == "bb" and e.server.id == "231823001912475648":
                    self.emojiBoatEndL = str(e)
                elif e.name == "cc" and e.server.id == "231823001912475648":
                    self.emojiBoatEndR = str(e)
                elif e.name == "dd" and e.server.id == "231823001912475648":
                    self.emojiBoatEndU = str(e)
                elif e.name == "ee" and e.server.id == "231823001912475648":
                    self.emojiBoatEndD = str(e)
                elif e.name == "ff" and e.server.id == "231823001912475648":
                    self.emojiBoatMidH = str(e)
                elif e.name == "gg" and e.server.id == "231823001912475648":
                    self.emojiBoatMidV = str(e)
                elif e.name == "uu" and e.server.id == "231823001912475648":
                    self.emojiUnknown = str(e)
                elif e.name == "AA" and e.server.id == "231823001912475648":
                    self.hEmojiWater = str(e)
                elif e.name == "BB" and e.server.id == "231823001912475648":
                    self.hEmojiBoatEndL = str(e)
                elif e.name == "CC" and e.server.id == "231823001912475648":
                    self.hEmojiBoatEndR = str(e)
                elif e.name == "DD" and e.server.id == "231823001912475648":
                    self.hEmojiBoatEndU = str(e)
                elif e.name == "EE" and e.server.id == "231823001912475648":
                    self.hEmojiBoatEndD = str(e)
                elif e.name == "FF" and e.server.id == "231823001912475648":
                    self.hEmojiBoatMidH = str(e)
                elif e.name == "GG" and e.server.id == "231823001912475648":
                    self.hEmojiBoatMidV = str(e)
                elif e.name == "UU" and e.server.id == "231823001912475648":
                    self.hEmojiUnknown = str(e)
            except StopIteration:
                break

    def getLetter(self, value):
        possibilities = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮"]
        return possibilities[value]

    def getValueAtBoardPosition(self, x, y, player):
        if x < 0 or y < 0 or x >= self.BOARD_SIZE or y >= self.BOARD_SIZE:
            return 0
        else:
            if player:
                return self.playerBoard[x][y]
            else:
                return self.botBoard[x][y]

    def generateTileStringPlayer(self, x, y):
        if self.playerBoard[x][y] == 0:  # live water
            return self.emojiWater
        elif self.playerBoard[x][y] == 1:  # dead water
            return self.hEmojiWater
        elif self.playerBoard[x][y] == 2:  # live boat
            if self.getValueAtBoardPosition(x - 1, y, True) in [2, 3, 5]:  # piece on left
                if self.getValueAtBoardPosition(x + 1, y, True) in [2, 3, 5]:
                    return self.emojiBoatMidH
                else:
                    return self.emojiBoatEndL
            elif self.getValueAtBoardPosition(x, y - 1, True) in [2, 3, 5]:  # piece on top
                if self.getValueAtBoardPosition(x, y + 1, True) in [2, 3, 5]:
                    return self.emojiBoatMidV
                else:
                    return self.emojiBoatEndU
            elif self.getValueAtBoardPosition(x + 1, y, True) in [2, 3, 5]:  # piece on right
                return self.emojiBoatEndR
            elif self.getValueAtBoardPosition(x, y + 1, True) in [2, 3, 5]:  # piece on bottom
                return self.emojiBoatEndD
            else:
                return self.emojiUnknown
        elif self.playerBoard[x][y] == 3 or self.playerBoard[x][y] == 5:  # dead boat
            if self.getValueAtBoardPosition(x - 1, y, True) in [2, 3, 5]:  # piece on left
                if self.getValueAtBoardPosition(x + 1, y, True) in [2, 3, 5]:
                    return self.hEmojiBoatMidH
                else:
                    return self.hEmojiBoatEndL
            elif self.getValueAtBoardPosition(x, y - 1, True) in [2, 3, 5]:  # piece on top
                if self.getValueAtBoardPosition(x, y + 1, True) in [2, 3, 5]:
                    return self.hEmojiBoatMidV
                else:
                    return self.hEmojiBoatEndU
            elif self.getValueAtBoardPosition(x + 1, y, True) in [2, 3, 5]:  # piece on right
                return self.hEmojiBoatEndR
            elif self.getValueAtBoardPosition(x, y + 1, True) in [2, 3, 5]:  # piece on bottom
                return self.hEmojiBoatEndD
            else:
                return self.hEmojiUnknown
        elif self.playerBoard[x][y] == 4:  # setup, one end selected
            return self.emojiUnknown
        else:
            return "⏹"

    def generateTileStringBot(self, x, y):
        if self.botBoard[x][y] == 0:  # live water
            return self.emojiWater
        elif self.botBoard[x][y] == 1:  # dead water
            return self.hEmojiWater
        elif self.botBoard[x][y] == 2:  # live boat
            return self.emojiWater      # hide ships
        elif self.botBoard[x][y] == 3:  # fully dead boat
            if self.getValueAtBoardPosition(x - 1, y, False) == 3:  # piece on left
                if self.getValueAtBoardPosition(x + 1, y, False) == 3:
                    return self.hEmojiBoatMidH
                else:
                    return self.hEmojiBoatEndL
            elif self.getValueAtBoardPosition(x, y - 1, False) == 3:  # piece on top
                if self.getValueAtBoardPosition(x, y + 1, False) == 3:
                    return self.hEmojiBoatMidV
                else:
                    return self.hEmojiBoatEndU
            elif self.getValueAtBoardPosition(x + 1, y, False) == 3:  # piece on right
                return self.hEmojiBoatEndR
            elif self.getValueAtBoardPosition(x, y + 1, False) == 3:  # piece on bottom
                return self.hEmojiBoatEndD
            else:
                return "⏹"
        elif self.botBoard[x][y] == 5:  # dead boat part
            return self.hEmojiUnknown   # don't reveal rest of ship
        else:
            return "⏹"

    def generateBoardStringPlayer(self):
        # message = "playerBoard:\n"
        # for i in range(len(self.playerBoard)):
        #     for j in range(len(self.playerBoard[i])):
        #         message += str(int(self.getValueAtBoardPosition(i, j, True))) + " "
        #     message += "\n"
        # message += "\n"
        # print(message)

        message = "⏹:one::two::three::four::five::six::seven::eight::nine:\n"
        for i in range(len(self.playerBoard)):
            message += self.getLetter(i)
            for j in range(len(self.playerBoard[i])):
                message += self.generateTileStringPlayer(j, i)
            message += "\n"
        return message

    def generateBoardStringBot(self):
        # message = "botBoard:\n"
        # for i in range(len(self.playerBoard)):
        #     for j in range(len(self.playerBoard[i])):
        #         message += str(int(self.getValueAtBoardPosition(i, j, False))) + " "
        #     message += "\n"
        # message += "\n"
        # print(message)

        message = "⏹:one::two::three::four::five::six::seven::eight::nine:\n"
        for i in range(len(self.botBoard)):
            message += self.getLetter(i)
            for j in range(len(self.botBoard[i])):
                message += self.generateTileStringBot(j, i)
            message += "\n"
        return message
