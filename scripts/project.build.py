from asyncio.subprocess import STDOUT,PIPE
from typing import Dict
from pathlib import WindowsPath
from subprocess import run
import os
import sys
import re
import hashlib
import logging

def check_paths(paths:Dict[str,WindowsPath]):
    for i in paths:
        if i.startswith("gen_") == False:
            if paths[i].exists() == False:
                return False
    return True

def clear(buildpath:WindowsPath):
    logging.info(f"Clear {buildpath}")
    if buildpath.exists():
        files_to_clean = os.listdir(buildpath)
        files_removed = 0
        for i in files_to_clean:
            _file = buildpath.joinpath(i)
            logging.debug(f"Removing file {_file}")
            try:
                os.remove(_file)
                files_removed+=1
            except OSError as err:
                logging.warning(f"Error '{err.strerror}' when trying to remove: {_file}")
        logging.info(f"Files Removed: {files_removed}")
    else:
        os.mkdir(buildpath)
        logging.info(f"Build directory created!")


commonCompileOptions = [
    "/c",                   # Compile only
    "/nologo",
    "/utf-8",               # Encoding
    "/ZI",                  #
    "/diagnostics:column",  # Show diagnostic in columns
    "/std:c++17",           # c++17
    "/W4",                  # All Warnings
    "/Od",                  # No Optimize
    "/D _DEBUG",            # Debug definition.
    "/D _WINDOWS",          #
    "/D _UNICODE",          #
    "/D UNICODE",           #
    "/Gm-",                 #
    "/EHsc",                # Exceptions
    "/fp:precise",          # Float precision
    "/MDd",                 #
    "/external:W4",         #
    "/FC",                  #
    "/errorReport:prompt"   # Promp when errors apper
]

def precompile(paths:Dict[str,WindowsPath]):
    logging.info("Precompiling")
    # Prepare arguments
    extraOptions = [
        f"/Yc{paths['pch.h'].name}",   # Create Precompiled
        f"/Fp{paths['gen_pre_pch']}",  # Precompiled File
        f"/Fd{paths['gen_pdb']}",      # Database File
        f"/Fo{paths['gen_pch']}",      # Object File
    ]
    file_path = f"{paths['pch.cpp']}"
    _ppch= [f"{paths['compiler']}",*commonCompileOptions,*extraOptions,file_path]
    logging.debug(f"Compiler Args: \n{''.join([i+' ' for i in _ppch])}")
    # Run compiler
    compile_pch = run(_ppch,
        stdout=PIPE,
        stderr=STDOUT,
        encoding='UTF-8',
        errors='ignore',
        capture_output=False,
        cwd=f"{paths['source']}"
    )
    # Logging
    if compile_pch.returncode == 0:
        logging.info(f"Precompiled Success [{compile_pch.returncode}]")
        logging.debug(f"Precompiled stdout:\n{compile_pch.stdout}")
    else:
        logging.error(f"Precompiled Error Code [{compile_pch.returncode}]")
        logging.debug(f"Precompiled Error:\n{compile_pch.stdout}")
    # End and return error code
    return compile_pch.returncode

def compile(paths:Dict[str,WindowsPath],file:WindowsPath,buildfile:WindowsPath):
    logging.info("Compiling")
    # Compiler custom arguments
    pch_use = paths['pch.h'].name
    extraOptions = [
        f"/I{paths['source'].joinpath('./utils/')}\\",  # Add aditional include dir
        f"/Yu{pch_use}",                                # Use Precompiled .h
        f"/Fp{paths['gen_pre_pch']}",                   # Use Precompiled .pch
        f"/Fd{paths['gen_pdb']}",                       # Database File
        f"/Fo{buildfile}",                              # Object File
    ]
    file_path = f"{file}"
    compiler_args= [f"{paths['compiler']}",*commonCompileOptions,*extraOptions,file_path]
    logging.debug(f"Compiler Args: \n{''.join([i+' ' for i in compiler_args])}")
    # Run compiler
    compile_file = run(compiler_args,
        stdout=PIPE,
        stderr=STDOUT,
        encoding='UTF-8',
        errors='ignore',
        capture_output=False,
        cwd=f"{paths['source']}"
    )
    # Logging
    if compile_file.returncode == 0:
        logging.info(f"Compiled Success Code [{compile_file.returncode}]")
        logging.debug(f"Compiled stdout:\n{compile_file.stdout}")
    else:
        logging.error(f"Compiled Error Code [{compile_file.returncode}]")
        logging.debug(f"Compiled Error:\n{compile_file.stdout}")
    # End and return error code
    return compile_file.returncode

def link(paths:Dict[str,WindowsPath]):
    logging.info("Linking")
    # Linker Arguments
    link_args =[
        "/ERRORREPORT:PROMPT",
        "/nologo",
        f"/OUT:{paths['gen_exe']}",
        "/INCREMENTAL",
        f"/ILK:{paths['gen_ilk']}",
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
        f"/PDB:{paths['gen_pdb']}",
        "/SUBSYSTEM:CONSOLE",
        "/TLBID:1",
        "/DYNAMICBASE",
        "/NXCOMPAT",
        f"/IMPLIB:{paths['gen_lib']}",
        "/MACHINE:X64",
    ]
    # Compiled objs to link
    obj_main = f"{paths['gen_main']}"
    obj_ppch = f"{paths['gen_pch']}"
    obj_util = f"{paths['gen_util']}"
    linker_args= [f"{paths['linker']}",*link_args,obj_main,obj_ppch,obj_util]
    logging.debug(f"Linker Args: \n{''.join([i+' ' for i in linker_args])}")
    # Run compiler
    link_exe = run(linker_args,
        stdout=PIPE,
        stderr=STDOUT,
        encoding='UTF-8',
        errors='ignore',
        capture_output=False,
        cwd=f"{paths['source']}"
    )
    # Logging
    if link_exe.returncode == 0:
        logging.info(f"Linked Success Code [{link_exe.returncode}]")
        logging.debug(f"Linked stdout:\n{link_exe.stdout}")
    else:
        logging.error(f"Linked Error Code [{link_exe.returncode}]")
        logging.debug(f"Linked Error:\n{link_exe.stdout}")
    # End and return error code
    return link_exe.returncode

#
# Script Only for Build
#
if __name__ == "__main__":

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
        level=logging.DEBUG,
        format=format_log,
        encoding="utf8",
    )

    logging.info(msg=f"Build Command {'None' if sys.argv.__len__()==1 else ''.join(sys.argv[1:])}")

    # Only work in windows
    if  sys.platform != "win32":
        logging.error("Script only for windows!")
        exit(1)

    # Project Directories
    source_directory = WindowsPath(__file__).parent.parent
    build_directory = source_directory.joinpath("./build/")

    # Compiler and Linker
    vc_path = os.getenv("VCToolsInstallDir")
    if vc_path is None:
        logging.error("Environment Variable 'VCToolsInstallDir' not found!")
        exit(1)

    project_paths = {
        "source": source_directory,
        "build": build_directory,
        "gen_exe": build_directory.joinpath("./app.exe"),
        "gen_pdb": build_directory.joinpath("./app.pdb"),
        "gen_ilk": build_directory.joinpath("./app.ilk"),
        "gen_lib": build_directory.joinpath("./app.lib"),
        "gen_main": build_directory.joinpath("./main.obj"),
        "gen_util": build_directory.joinpath("./util.obj"),
        "gen_pch": build_directory.joinpath("./pch.obj"),
        "gen_pre_pch": build_directory.joinpath("./pch.pch"),
        "compiler": WindowsPath(vc_path).joinpath("./bin/HostX64/x64/cl.exe"),
        "linker": WindowsPath(vc_path).joinpath("./bin/HostX64/x64/link.exe"),
        "main.cpp":source_directory.joinpath("./main.cpp"),
        "util.cpp":source_directory.joinpath("./utils/util.cpp"),
        "utils.h":source_directory.joinpath("./utils/utils.h"),
        "pch.cpp":source_directory.joinpath("./pch.cpp"),
        "pch.h":source_directory.joinpath("./pch.h"),
    }


    # Check Existence of all paths
    pp_log = ""
    for i in project_paths.values():
        pp_log = pp_log +f"\n{i}"
    logging.debug(f"Project paths:{pp_log}")
    check_res = check_paths(project_paths)
    if check_res == False:
        logging.error("One or more paths not exist!")
        exit(1)

    # Hash
    #with open(project_paths["main.cpp"],mode="r",encoding="utf8") as fp:
    #    print(hashlib.sha1(fp.read().encode(encoding="utf8")).hexdigest())

    # Script options:
    if sys.argv.__len__() > 1:

        # Clean all
        if  re.match(r"^clear$",sys.argv[1],flags=re.IGNORECASE) is not None:
            clear(project_paths["build"])

        # Precompile files
        if  re.match(r"^precompile$",sys.argv[1],flags=re.IGNORECASE) is not None:
            precompile(project_paths)

        # Compile and link
        if  re.match(r"^compile$",sys.argv[1],flags=re.IGNORECASE) is not None:
            _c1 = compile(project_paths,project_paths["main.cpp"],project_paths["gen_main"])
            _c2 = compile(project_paths,project_paths["util.cpp"],project_paths["gen_util"])
        # Link only
        if  re.match(r"^link$",sys.argv[1],flags=re.IGNORECASE) is not None:
            link(project_paths)
