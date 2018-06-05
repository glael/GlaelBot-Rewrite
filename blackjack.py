import discord
import random


class BlackJack:
    cardTypes = ["♠", "♥", "♣", "♦"]

    def __init__(self, in_economy_manager):
        self.MinutesUntilDelete = 10
        self.players = []
        self.playerCards = []
        self.playerBets = []
        self.cardsOut = []
        self.standingPlayers = []
        self.doubledPlayers = []
        self.winnings = {}
        self.inputToFuncDic = {}
        self.currentPlayer = 1
        self.finished = False
        self.startVotes = 0
        self.MinutesUntilDelete = 10
        self.playerCards.append([])
        self.playerBets.append(0)
        self.players.append("dealer")
        self.winnings["none"] = "0"
        self.startVotes = 0
        self.__build_dic()
        self.economy_manager = in_economy_manager

    def __del__(self):
        self.MinutesUntilDelete = 0
        self.playerCards.clear()
        self.playerBets.clear()
        self.cardsOut.clear()
        self.standingPlayers.clear()
        self.players.clear()
        self.winnings.clear()
        self.inputToFuncDic.clear()

    # returns when start is called, open for expansion
    def start(self):
        return "press X to start"

    # starts a round, clears all applicable lists and rebuilds where necessary
    def __start_round(self):
        self.startVotes += 1
        if self.startVotes == len(self.players) - 1:
            self.startVotes = 0
            self.playerCards.clear()
            self.doubledPlayers.clear()
            self.winnings.clear()
            self.cardsOut.clear()
            self.standingPlayers = []
            for i in range(0, len(self.players)):
                self.playerCards.append([])
                x = self.__randomCard()
                (self.playerCards[i]).append(x)
            self.currentPlayer = 1
            self.finished = False

    # beats current player till he's dead, jk, it gives him/her a card
    def __player_hit(self):
        x = self.__randomCard()
        (self.playerCards[self.currentPlayer]).append(x)
        self.currentPlayer = self.find_next_player()


    # current player won't receive any more cards
    def __player_stand(self):
        self.standingPlayers.append(self.players[self.currentPlayer])
        self.currentPlayer = self.find_next_player()

    # gives the current player a card, and stops them from receiving future cards
    def __player_double(self):
        self.doubledPlayers.append(self.currentPlayer)
        (self.playerCards[self.currentPlayer]).append(self.__randomCard())
        self.__player_stand()

    # returns a random card that hasn't been taken from the deck
    def __randomCard(self):
        x = 0
        if len(self.cardsOut) == 0:
            x = random.randint(0, 51)
        else:
            x = self.cardsOut[0]
            # this can't be infinite loop with how it is set up, in worst case 1 player has all 1,2 and 3 3's ,
            # which rules out all players having a lot of cards, in very very worst case this could ofcourse be infinite
            # but that is extremely rare
            while x in self.cardsOut:
                x = random.randint(0, 51)
        self.cardsOut.append(x)
        return x

    # returns the next player number that does not have more than 21 or stands
    def find_next_player(self):
        x = (self.currentPlayer + 1) % len(self.players)
        if x == 0:
            x = 1
        while self.player_card_total_under21(x) >= 21 or self.players[x] in self.standingPlayers:
            x = (x + 1) % len(self.players)
            if x == 0:
                x = 1
            if x == self.currentPlayer and (self.player_card_total_under21(x) >= 21 or self.players[x] in self.standingPlayers):
                x = 1
                self.dealer_turn()
                break
        return x

    # gives the dealer all his cards, and spreads the winnings
    def dealer_turn(self):
        while self.player_card_total_under21(0) < 17:
            x = self.__randomCard()
            (self.playerCards[0]).append(x)
        self.spread_winnings()
        self.finished = True

    # calculates the card total for a player, aces will be chosen so that it is closes to 21
    def player_card_total_under21(self, playernum):
        amountOfAces = 0
        total = 0
        for i in self.playerCards[playernum]:
            card = self.get_card_rank(i)
            try:

                card = int(card)
                if card == 1:
                    amountOfAces += 1
                else:
                    total += card
            except ValueError:
                total += 10
        if amountOfAces > 0:
            for i in range(amountOfAces):
                if (total + (11 * (amountOfAces - i)) + i) <= 21:
                    total += (11 * (amountOfAces - i)) + i
                    break
            else:  # yes this is indeed a for-else
                total += amountOfAces
        return total

    # calls the function for the input
    def received_input(self, letter, playername):
        if playername == self.players[self.currentPlayer]:
            self.inputToFuncDic[letter]()
            self.MinutesUntilDelete = 10
        elif letter == "x" and playername in self.players:
            self.__start_round()
            self.MinutesUntilDelete = 10


    # builds the embed of the current game state
    def build_embed(self):
        messageEmbed = discord.Embed()
        messageEmbed.title = "BlackJack"
        messageEmbed.colour = discord.Colour.dark_purple()
        if len(self.winnings) == 0:
            description = "```"
            description += self.build_dealerLines()
            description += "\n \n \n"
            description += self.build_playerPointerLine() + "\n \n"
            description += self.build_playerLines()
            messageEmbed.description = description + "```"
        else:
            description = "```"
            description += self.build_dealerLines()
            description += "\n \n \n"
            description += "----------------------------------------"
            description += "```" + self.build_winner_lines() + "```"
            description += "---------------------------------------- \n"
            description += self.build_playerLines() + "```"
            messageEmbed.description = description
        return messageEmbed


    # builds the lines with the winners
    def build_winner_lines(self):
        desc = ""
        for key, value in self.winnings.items():
            desc += key + " : " + value + "\n"
        return desc

    # builds the lines for the dealer
    def build_dealerLines(self):
        description = ""
        # center the dealer's cards
        center = (" " * int(len(self.players) / 2))

        # if he has no cards yet
        if len(self.playerCards[0]) == 0:
            description += center + "x" + "\n"
            description += center + "x"
        else:
            lineOne = center
            lineTwo = center
            for i in self.playerCards[0]:
                lineOne += self.cardTypes[int(i / 13)]
                # calculates the card type from the card number 1 is ace of spades, 14 is ace of hearts etc
                lineTwo += self.get_card_rank(i)
            description += lineOne + "\n" + lineTwo + "\n"
        return description


    # builds the line with the current playername
    def build_playerPointerLine(self):
        return "```" + "turn: " + self.players[self.currentPlayer] + "```"


    # builds the lines with the player cards and names, formatting for growing card numbers not on point yet
    def build_playerLines(self):
        max_name_length = 5
        playerLine1 = ""
        playerLine2 = ""
        playerLine3 = ""
        for i in range(1, len(self.players)):
            playerLine1Addition = ""
            playerLine2Addition = ""
            namelen = max_name_length - len(self.playerCards[i]) if len(self.playerCards[i]) < max_name_length else 0
            cardlen = len(self.playerCards[i]) - max_name_length if len(self.playerCards[i]) > max_name_length else 0

            if len(self.playerCards[i]) == 0:
                playerLine1Addition = " " + "x" + int(namelen) * " "
                playerLine2 += " " + "x" + int(namelen) * " "
            else:
                playerLine1Addition = " "
                playerLine2Addition = " "
                for card in self.playerCards[i]:
                    playerLine1Addition += self.cardTypes[int(card / 13)]
                    playerLine2Addition += self.get_card_rank(card)
                playerLine1Addition += int(namelen) * " "
                playerLine2Addition += int(namelen) * " "

            playerLine1 += playerLine1Addition
            playerLine2 += playerLine2Addition
            playerLine3 += "|"
            playerLine3 += self.players[i].ljust(5)[:5]
            playerLine3 += " " * cardlen
        return playerLine1 + "\n" + playerLine2 + "\n" + playerLine3


    # calculates and gives the players their winnings
    def spread_winnings(self):
        dealerTotal = self.player_card_total_under21(0)
        for i in range(1, len(self.players)):
            x = self.player_card_total_under21(i)
            multiplier = 1
            if i in self.doubledPlayers:
                multiplier = 2
            if x <= 21:
                if x > dealerTotal:
                    if len(self.playerCards[i]) == 2 and x == 21:
                        self.__player_balance_edit(i, self.playerBets[i] * multiplier * 1.5)
                        self.winnings[self.players[i]] = "Blackjack!: " + str(self.playerBets[i] * 1.5 * multiplier)
                    else:
                        self.__player_balance_edit(i, self.playerBets[i] * 1 * multiplier)
                        self.winnings[self.players[i]] = "winner! " + str(self.playerBets[i] * 1 * multiplier)
                elif x == dealerTotal:
                    if len(self.playerCards[i]) == 2 and x == 21 and len(self.playerCards[0]) > 2:
                        self.__player_balance_edit(i, self.playerBets[i] * 1.5 * multiplier)
                        self.winnings[self.players[i]] =  "Blackjack! " + str(self.playerBets[i] * 1.5 * multiplier)
                    else:
                        self.winnings[self.players[i]] = "even.. 0"
                elif x < dealerTotal <= 21:
                    self.__player_balance_edit(i, self.playerBets[i] * -1 * multiplier)
                    self.winnings[self.players[i]] = "LOSER " + str(self.playerBets[i] * -1 * multiplier)
                elif x < dealerTotal and dealerTotal > 21:
                    self.__player_balance_edit(i, self.playerBets[i] * 1 * multiplier)
                    self.winnings[self.players[i]] = "Winner " + str(self.playerBets[i] * 1 * multiplier)
            else:
                self.__player_balance_edit(i, self.playerBets[i] * -1 * multiplier)
                self.winnings[self.players[i]] = "LOSER" + str(self.playerBets[i] * -1 * multiplier)

    # edits a player's balance
    def __player_balance_edit(self, player_num, amount):
        print(str(self.players[player_num]))
        self.economy_manager.increase_balance_of_player_unknown_id(self.players[player_num], amount)


    # transforms a card number to it's rank
    def get_card_rank(self, number):
        x = (number % 13) + 1
        if x >= 10:
            if x == 10:
                return "t"
            elif x == 11:
                return "J"
            elif x == 12:
                return "Q"
            elif x == 13:
                return "K"
        else:
            return str(x)


    # adds a player to the game
    def addPlayer(self, sender, amount):
        if((sender.name) not in self.players):
            self.players.append(sender.name)
            self.playerCards.append([])
            self.playerBets.append(amount)
            return "You're in!"
        else:
            return "you already entered! :angry:"

    # builds the dictionary with "reaction" -> function
    def __build_dic(self):
        self.inputToFuncDic = {
            "x": self.__start_round,
            "h": self.__player_hit,
            "d": self.__player_double,
            "s": self.__player_stand
        }

    # returns the reactions that need to be displayed now
    def get_reactions(self):
        if len(self.winnings) == 0 and not self.finished:
            return ["h", "s", "d"]
        elif len(self.winnings) != 0 and not self.finished:
            return ["x"]
        elif self.finished:
            return ["x", "r"]
