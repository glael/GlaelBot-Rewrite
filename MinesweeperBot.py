from random import randint
class MinesweeperBot:
    def __init__(self, in_bot):
        self.bot = in_bot
        self.BOARD_SIZE = 10
        self.AMOUNT_OF_BOMBS = 20
        self.BOMB = -1
        self.zero = ""
        self.one = ""
        self.two = ""
        self.three = ""
        self.four = ""
        self.five = ""
        self.six = ""
        self.seven = ""
        self.eight = ""
        self.bomb = ""


    def generateEmoji(self): # call in on_ready()
        emoji = self.bot.get_all_emojis()
        while True:
            try:
                e = next(emoji)
                if e.name == "0_" and e.server.id == "231823001912475648":
                    self.zero = str(e)
                elif e.name == "1_" and e.server.id == "231823001912475648":
                    self.one = str(e)
                elif e.name == "2_" and e.server.id == "231823001912475648":
                    self.two = str(e)
                elif e.name == "3_" and e.server.id == "231823001912475648":
                    self.three = str(e)
                elif e.name == "4_" and e.server.id == "231823001912475648":
                    self.four = str(e)
                elif e.name == "5_" and e.server.id == "231823001912475648":
                    self.five = str(e)
                elif e.name == "6_" and e.server.id == "231823001912475648":
                    self.six = str(e)
                elif e.name == "7_" and e.server.id == "231823001912475648":
                    self.seven = str(e)
                elif e.name == "8_" and e.server.id == "231823001912475648":
                    self.eight = str(e)
                elif e.name == "B_" and e.server.id == "231823001912475648":
                    self.bomb = str(e)
            except StopIteration:
                break


    def count_adjacent_bombs(self, field, column, row, width, height):
        counter = 0
        for check_column in range(column-1, column + 2):
            for check_row in range(row - 1, row + 2):
                if check_column >= 0 and check_row >= 0 and check_column < width and check_row < height:
                    if field[check_row][check_column] == self.BOMB:
                        counter += 1

        return counter


    def generate_minefield(self, width, height, bomb_count):
        """
        Generates a matrix of widht x height
        Each cell is a tile of the field
        bombs are -1
        other values are the number of adjacent bombs
        """

        # Caputre overflow
        if bomb_count > width * height:
            return [[0 for column in range(self.BOMB * width)] for row in range(self.BOMB * height)]

        field = [[0 for column in range(width)] for row in range(height)]

        # Place bombs
        for bomb in range(bomb_count):
            while True:
                column = randint(0, width-1)
                row = randint(0, height-1)

                if field[row][column] != self.BOMB:
                    field[row][column] = self.BOMB
                    break

        # Place indicators
        for row in range(height):
            for column in range(width):
                if field[row][column] != self.BOMB:
                    field[row][column] = self.count_adjacent_bombs(field, column, row, width, height)
        return field

    async def print_minefield(self, ctx, *args):
        message = ""
        field = self.generate_minefield(self.BOARD_SIZE, self.BOARD_SIZE, self.AMOUNT_OF_BOMBS)
        for x in range(len(field)):
            for y in range(len(field[x])):
                if field[x][y] == self.BOMB:
                    message += "||" + self.bomb + "||"
                elif field[x][y] == 0:
                    message += "||" + self.zero + "||"
                elif field[x][y] == 1:
                    message += "||" + self.one + "||"
                elif field[x][y] == 2:
                    message += "||" + self.two + "||"
                elif field[x][y] == 3:
                    message += "||" + self.three + "||"
                elif field[x][y] == 4:
                    message += "||" + self.four + "||"
                elif field[x][y] == 5:
                    message += "||" + self.five + "||"
                elif field[x][y] == 6:
                    message += "||" + self.six + "||"
                elif field[x][y] == 7:
                    message += "||" + self.seven + "||"
                elif field[x][y] == 8:
                    message += "||" + self.eight + "||"
            await self.bot.send_message(ctx.message.channel, message)
            message = ""
