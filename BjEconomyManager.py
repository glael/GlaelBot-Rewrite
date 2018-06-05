import datetime
import pickle


# noinspection PyMethodMayBeStatic
class BjEconomyManager:
    def __init__(self):
        self.economyDict = self.read_economy()

    def read_economy(self):
        try:
            f = open('/home/pi/Documents/glaelbot/economy.txt', 'rb')
            return pickle.load(f)
        except EOFError:
            print("FileIO error: the file was empty " + 'economy.txt')
            return []
        except FileNotFoundError:
            print("FileIO error: the file was not found: " + 'economy.txt')
            return []

    def store_economy(self):
        with open('/home/pi/Documents/glaelbot/economy.txt', 'wb') as output:
            pickle.dump(self.economyDict, output, pickle.HIGHEST_PROTOCOL)
            print("dumped")
        print("test")

    def get_balance_of_player(self, player_id):
        for row in self.economyDict:
            if row[0] == player_id:
                return row[3]
        return 0

    def get_last_time_economy_received(self, player_id):
        for row in self.economyDict:
            if row[0] == player_id:
                return row[2]
        return datetime.datetime.now() - datetime.timedelta(days=5)

    def reset_last_time_economy_received(self, player_id, player_name):
        for row in range(len(self.economyDict)):
            if self.economyDict[row][0] == player_id:
                self.economyDict[row][2] = datetime.datetime.now()
                self.economyDict[row][1] = player_name
                self.store_economy()
                return
        self.economyDict.append([player_id, player_name, (datetime.datetime.now() - datetime.timedelta(days=5)), 0])
        self.store_economy()

    def exists(self, player_id):
        for row in self.economyDict:
            if row[0] == player_id:
                return True
        return False

    def set_balance_of_player(self, player_id, balance, player_name):
        for row in range(len(self.economyDict)):
            if self.economyDict[row][0] == player_id:
                self.economyDict[row][3] = balance
                self.economyDict[row][1] = player_name
                self.store_economy()
                return
        self.economyDict.append([player_id, player_name, (datetime.datetime.now() - datetime.timedelta(days=5)), balance])
        self.store_economy()

    def increase_balance_of_player(self, player_id, amount, player_name):
        current_balance = self.get_balance_of_player(player_id)
        if amount >= 0 or abs(amount) <= current_balance:
            self.set_balance_of_player(player_id, current_balance + amount, player_name)
        else:
            raise ValueError("Balance too low!")

    def get_balance_of_player_unknown_id(self, player_name):
        for row in self.economyDict:
            if row[1] == player_name:
                return row[3]
        return 0

    def set_balance_of_player_unknown_id(self, player_name, balance):
        for row in range(len(self.economyDict)):
            if self.economyDict[row][1] == player_name:
                self.economyDict[row][3] = balance
                self.store_economy()
                return
        return

    def increase_balance_of_player_unknown_id(self, player_name, amount):
        current_balance = self.get_balance_of_player_unknown_id(player_name)
        if amount >= 0 or abs(amount) <= current_balance:
            self.set_balance_of_player_unknown_id(player_name, current_balance + amount)
        else:
            raise ValueError("Balance too low!")

    def get_list_of_balances(self):
        result = "The current rankings are:\n"
        for row in sorted(self.economyDict, reverse=True, key=lambda x: x[3]):
            result += row[1] + ": " + str(row[3]) + "\n"
        return result



