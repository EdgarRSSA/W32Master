# @file project.build.py
#
# @author Edgar Rosales
# @brief Script for build C++ MSVC code
# @version 0.1
# @date 2022-07-05#
#
# @copyright Copyright (c) 2022

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
            exit(1)
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


def command(argument:str, cmd:str):
    regex = re.compile(f"^{cmd}$",re.IGNORECASE)
    if  regex.match(argument) is not None:
        return True
    return False


#
# Script Only for Build
#
if __name__ == "__main__":

    # Config logging
    ProjectBuild.loggingConfig()

    # Command to execute
    logging.info(f"Build Command {'None' if sys.argv.__len__()==1 else ''.join(sys.argv[1:])}")

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
        "gen_main_prep": project.build.joinpath("./main_prep.i"),
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

        # Clear all
        if  command(sys.argv[1],"clear"):
            project.clearBuildDirectory()

        # Precompile files
        if  command(sys.argv[1],"precompile"):
            logging.info("Precompiling: pch , utils ")
            project.compile([
                *commonCompileOptions,
                f"/Yc{project_paths['pch.h'].name}",   # Create Precompiled
                f"/Fp{project_paths['gen_pre_pch']}",  # Precompiled File
                f"/Fd{project_paths['gen_pdb']}",      # Database File
                f"/Fo{project.build}\\",               # Object File
                f"/I{project_paths['utils']}\\",       # Include utils dir
                f"/I{project.source}\\",               # Include source dir
                f"{project_paths['pch.cpp']}",         # pch.cpp
                f"{project_paths['util.cpp']}",        # util.cpp

            ])

        # Compile and link
        if  command(sys.argv[1],"compile"):
            logging.info("Compiling: main")
            project.compile([
                *commonCompileOptions,
                f"/Yu{project_paths['pch.h'].name}",  # Use Precompiled header
                f"/Fp{project_paths['gen_pre_pch']}", # Use Precompiled File
                f"/Fd{project_paths['gen_pdb']}",     # Database File
                f"/Fo{project_paths['gen_main']}",    # Object File
                f"/I{project_paths['utils']}\\",      # Add aditional include dir
                f"/I{project.source}\\",              # Include source dir
                f"{project_paths['main.cpp']}"        # pch.cpp
            ])

        # Preprocess
        if  command(sys.argv[1],"preprocess"):
            project.compile([
                *commonCompileOptions[1:],
                "/P",
                "/C",
                f"/Yu{project_paths['pch.h'].name}",  # Use Precompiled header
                f"/Fp{project_paths['gen_pre_pch']}", # Use Precompiled File
                f"/Fd{project_paths['gen_pdb']}",     # Database File
                f"/Fo{project_paths['gen_main']}",    # Object File
                f"/Fi{project_paths['gen_main_prep']}",    # Preprocessed File
                f"/I{project_paths['utils']}\\",      # Add aditional include dir
                f"{project_paths['main.cpp']}"        # pch.cpp
            ])

        # Link only
        if  command(sys.argv[1],"link"):
            logging.info("Linking: app.exe")
            # Linker Arguments
            link_args =[
                "/ERRORREPORT:PROMPT",                  # Prompt when error
                "/nologo",                              # No banner
                "/INCREMENTAL",                         # Incrmental link
                "/MANIFEST:EMBED",                      # Manifest
                "/MANIFESTUAC:level='asInvoker' uiAccess='false'",  # Runs at the same permission level as the process that started it
                "/DEBUG",                               # Debug info
                "/SUBSYSTEM:CONSOLE",                   # CONSOLE TYPE
                "/TLBID:1",                             # Linker-created type library
                "/DYNAMICBASE",                         # Application should be randomly rebased at load time. default.
                "/NXCOMPAT",                            # Data Execution Prevention
                "/MACHINE:X64",                         # x64 only
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
                f"/ILK:{project_paths['gen_ilk']}",     # Link Incremental file
                f"/OUT:{project_paths['gen_exe']}",     # EXE
                f"/PDB:{project_paths['gen_pdb']}",     # PDB
                f"/IMPLIB:{project_paths['gen_lib']}",  # Generated LIB
                f"{project_paths['gen_pch']}",          # pch.obj to link
                f"{project_paths['gen_main']}",         # main.obj to link
                f"{project_paths['gen_util']}",         # util.obj to link
            ]
            project.link(link_args)
