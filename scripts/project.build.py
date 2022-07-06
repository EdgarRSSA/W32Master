from asyncio.subprocess import STDOUT,PIPE
from typing import Dict, List
from pathlib import WindowsPath
from subprocess import run
import os
import sys
import re
import hashlib
import logging

class ProjectBuild:
    """ Project """

    source:WindowsPath
    build:WindowsPath
    compiler:WindowsPath
    linker:WindowsPath

    @classmethod
    def __init__(
        self,*,
        source:WindowsPath,
        build:WindowsPath
    ) -> None:
        """ Initialize or Exit when error """
        # Compiler and Linker
        vc_path = os.getenv("VCToolsInstallDir")
        if vc_path is None:
            logging.error("Environment Variable 'VCToolsInstallDir' not found!")
            exit(1)
        self.source = source
        self.build = build
        self.compiler = WindowsPath(vc_path).joinpath("./bin/HostX64/x64/cl.exe")
        self.linker = WindowsPath(vc_path).joinpath("./bin/HostX64/x64/link.exe")
        # Check paths
        for i in [self.source,self.compiler,self.linker]:
            if not i.exists():
                logging.error(f"Path not exist: {i}")
                exit(1)
        # Create build path if not exist
        if not self.build.exists():
            logging.info(f"Created build directory.")
            os.mkdir(self.build)
        # Logs
        logging.debug(f"Source   {self.source}")
        logging.debug(f"Build    {self.build}")
        logging.debug(f"Compiler {self.compiler}")
        logging.debug(f"Linker   {self.linker}")

    @staticmethod
    def loggingConfig():
        # Check if parent process is powershell and
        # change format used by the logger if true.
        parent_exe = run(['tasklist.exe','/NH','/svc','/FO','CSV','/FI',f"PID eq {os.getppid()}"],
            stdout=PIPE,
            stderr=STDOUT,
            encoding='UTF-8',
            errors='ignore',
            capture_output=False,
        )
        format_log = "%(asctime)s %(levelname)-8s %(message)s"
        if (parent_exe.returncode == 0):
            parent_name = parent_exe.stdout.split(",")[0].replace("\"","")
            if parent_name.startswith("pwsh") or parent_name.startswith("powershell"):
                time_color = "\u001b[38;5;220m"
                reset_color = "\u001b[0m"
                level_color = "\u001b[38;5;219m"
                format_log = "{0}%(asctime)s{1} %(levelname)-8s{2} %(message)s".format(time_color,level_color,reset_color)
        # Logging Config
        logging.basicConfig(
            level=logging.INFO,
            format=format_log,
            encoding="utf8",
        )

    @classmethod
    def compile(self, arguments:List[str]):
        compiler_args= [f"{self.compiler}",*arguments]
        logging.debug(f"Compiler Arguments: \n{''.join([i+' ' for i in compiler_args])}")
        # Run compiler
        compile_file = run(compiler_args,
            stdout=PIPE,
            stderr=STDOUT,
            encoding='UTF-8',
            errors='ignore',
            capture_output=False,
            cwd=f"{self.source}"
        )
        # Logging
        if compile_file.returncode == 0:
            logging.info(f"Compiler Success")
            logging.info(f"Compiler stdout:\n{compile_file.stdout}")
        else:
            logging.error(f"Compiler Error Code [{compile_file.returncode}]")
            logging.error(f"Compiler Error:\n{compile_file.stdout}")
            exit(1) # Error

    @classmethod
    def link(self,arguments:List[str]):
        linker_args= [f"{self.linker}",*arguments]
        logging.debug(f"Link Arguments:\n{''.join([i+' ' for i in linker_args])}")
        # Run compiler
        link_exe = run(linker_args,
            stdout=PIPE,
            stderr=STDOUT,
            encoding='UTF-8',
            errors='ignore',
            capture_output=False,
            cwd=f"{self.source}"
        )
        # Logging
        if link_exe.returncode == 0:
            logging.info(f"Link Success")
            logging.info(f"Link Stdout:\n{link_exe.stdout}")
        else:
            logging.error(f"Link Error Code [{link_exe.returncode}]")
            logging.error(f"Link Error:\n{link_exe.stdout}")
        # End and return error code
        return link_exe.returncode

    @classmethod
    def clearBuildDirectory(self):
        logging.info(f"Clear Directory: {self.build}")
        files_to_clean = os.listdir(self.build)
        files_removed = 0
        for i in files_to_clean:
            _file = self.build.joinpath(i)
            logging.debug(f"Removing file: {_file}")
            try:
                os.remove(_file)
                files_removed+=1
            except OSError as err:
                logging.warning(f"Error '{err.strerror}' when trying to remove: {_file}")
        logging.info(f"Files Removed: {files_removed}")


#
# Script Only for Build
#
if __name__ == "__main__":

    # Config logging
    ProjectBuild.loggingConfig()

    # Command to execute
    logging.info(msg=f"Build Command {'None' if sys.argv.__len__()==1 else ''.join(sys.argv[1:])}")

    # Project Tool Setup
    project = ProjectBuild(
        source=WindowsPath(__file__).parent.parent,
        build=WindowsPath(__file__).parent.parent.joinpath("./build/")
    )


    # Compiler Common arguments
    commonCompileOptions = [
        "/c",                   # Compile only
        "/nologo",              # No show compiler banner
        "/utf-8",               # Encoding
        "/ZI",                  # Debug info
        "/diagnostics:column",  # Show diagnostic in columns
        "/std:c++20",           # c++20
        "/W4",                  # All Warnings
        "/Od",                  # No Optimize
        "/D _DEBUG",            # Debug definition.
        "/D _WINDOWS",          #
        "/D _UNICODE",          #
        "/D UNICODE",           #
        "/EHsc",                # Exception handling
        "/fp:precise",          # Float precision
        "/MDd",                 # Debug multithread-specific
        "/external:W4",         # All warnings for external files
        "/FC",                  # Full path in diagnostics
        "/errorReport:prompt"   # Promp when error
    ]

    project_paths = {
        "gen_exe": project.build.joinpath("./app.exe"),
        "gen_pdb": project.build.joinpath("./app.pdb"),
        "gen_ilk": project.build.joinpath("./app.ilk"),
        "gen_lib": project.build.joinpath("./app.lib"),
        "gen_main": project.build.joinpath("./main.obj"),
        "gen_util": project.build.joinpath("./util.obj"),
        "gen_pch": project.build.joinpath("./pch.obj"),
        "gen_pre_pch": project.build.joinpath("./pch.pch"),
        "main.cpp": project.source.joinpath("./main.cpp"),
        "utils": project.source.joinpath("./utils/"),
        "util.cpp": project.source.joinpath("./utils/util.cpp"),
        "utils.h": project.source.joinpath("./utils/utils.h"),
        "pch.cpp": project.source.joinpath("./pch.cpp"),
        "pch.h": project.source.joinpath("./pch.h"),
    }


    # Hash
    #with open(project_paths["main.cpp"],mode="r",encoding="utf8") as fp:
    #    print(hashlib.sha1(fp.read().encode(encoding="utf8")).hexdigest())

    # Script options:
    if sys.argv.__len__() > 1:

        # Clean all
        if  re.match(r"^clear$",sys.argv[1],flags=re.IGNORECASE) is not None:
            project.clearBuildDirectory()

        # Precompile files
        if  re.match(r"^precompile$",sys.argv[1],flags=re.IGNORECASE) is not None:
            logging.info("Precompiling: pch ")
            project.compile([
                *commonCompileOptions,
                f"/Yc{project_paths['pch.h'].name}",   # Create Precompiled
                f"/Fp{project_paths['gen_pre_pch']}",  # Precompiled File
                f"/Fd{project_paths['gen_pdb']}",      # Database File
                f"/Fo{project_paths['gen_pch']}",      # Object File
                f"{project_paths['pch.cpp']}"          # pch.cpp
            ])

        # Compile and link
        if  re.match(r"^compile$",sys.argv[1],flags=re.IGNORECASE) is not None:
            logging.info("Compiling: main")
            project.compile([
                *commonCompileOptions,
                f"/Yu{project_paths['pch.h'].name}",  # Use Precompiled header
                f"/Fp{project_paths['gen_pre_pch']}", # Use Precompiled File
                f"/Fd{project_paths['gen_pdb']}",     # Database File
                f"/Fo{project_paths['gen_main']}",    # Object File
                f"/I{project_paths['utils']}\\",      # Add aditional include dir
                f"{project_paths['main.cpp']}"        # pch.cpp
            ])
            logging.info("Compiling: utils")
            project.compile([
                *commonCompileOptions,
                f"/Yu{project_paths['pch.h'].name}",  # Use Precompiled header
                f"/Fp{project_paths['gen_pre_pch']}", # Use Precompiled File
                f"/Fd{project_paths['gen_pdb']}",     # Database File
                f"/I{project_paths['utils']}\\",      # Add aditional include dir
                f"/Fo{project_paths['gen_util']}",    # Object File
                f"{project_paths['util.cpp']}"        # pch.cpp
            ])

        # Link only
        if  re.match(r"^link$",sys.argv[1],flags=re.IGNORECASE) is not None:
            logging.info("Linking: app.exe")
            # Linker Arguments
            link_args =[
                "/ERRORREPORT:PROMPT",
                "/nologo",
                f"/OUT:{project_paths['gen_exe']}",
                "/INCREMENTAL",
                f"/ILK:{project_paths['gen_ilk']}",
                #"dwmapi.lib",
                "kernel32.lib",
                "user32.lib",
                #"gdi32.lib",
                "winspool.lib",
                "comdlg32.lib",
                "advapi32.lib",
                "shell32.lib",
                "ole32.lib",
                "oleaut32.lib",
                "uuid.lib",
                "odbc32.lib",
                "odbccp32.lib",
                "/MANIFEST",
                "/MANIFESTUAC:level='asInvoker' uiAccess='false'",
                "/manifest:embed",
                "/DEBUG",
                f"/PDB:{project_paths['gen_pdb']}",
                "/SUBSYSTEM:CONSOLE",
                "/TLBID:1",
                "/DYNAMICBASE",
                "/NXCOMPAT",
                f"/IMPLIB:{project_paths['gen_lib']}",
                "/MACHINE:X64",
                f"{project_paths['gen_pch']}",
                f"{project_paths['gen_main']}",
                f"{project_paths['gen_util']}",
            ]
            project.link(link_args)
