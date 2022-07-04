from typing import Dict
from pathlib import WindowsPath
from subprocess import run
import os, sys, re, hashlib

def check_paths(paths:Dict[str,WindowsPath]):
    for i in paths:
        if i.startswith("gen_") == False:
            if paths[i].exists() == False:
                return False
    return True

def clear(buildpath:WindowsPath):
    print(f"\nClean directory: {buildpath}\n")
    if buildpath.exists():
        files_to_clean = os.listdir(buildpath)
        files_removed = 0
        for i in files_to_clean:
            _file = buildpath.joinpath(i)
            print(f"\tRemoving file {_file}")
            try:
                os.remove(_file)
                files_removed+=1
            except OSError as err:
                print(f"\tError '{err.strerror}' when trying to remove: {_file}")
        print(f"Files Removed: {files_removed}")
    else:
        os.mkdir(buildpath)
        print(f"Build directory created!")


commonCompileOptions = [
    "/c",                   # Compile only
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
    print("\nPrecompiling")
    extraOptions = [
            f"/Yc{paths['pch.h'].name}",   # Create Precompiled
            f"/Fp{paths['gen_pre_pch']}",  # Precompiled File
            f"/Fd{paths['gen_pdb']}",      # Database File
            f"/Fo{paths['gen_pch']}",      # Object File
        ]
    file_path = f"{paths['pch.cpp']}"
    _ppch= [f"{paths['compiler']}",*commonCompileOptions,*extraOptions,file_path]
    print(*_ppch,sep=" ")
    print()
    compile_pch = run(_ppch,capture_output=False,cwd=f"{paths['source']}")
    return compile_pch.returncode

def compile(paths:Dict[str,WindowsPath],file:WindowsPath,buildfile:WindowsPath):
    print("\nCompiling")
    level = file.relative_to(paths["source"]).parts.__len__() - 1
    pch_use = paths['pch.h'].name

    extraOptions = [
        f"/I{paths['source'].joinpath('./utils/')}\\",  # Add aditional include dir
        f"/Yu{pch_use}",                                # Use Precompiled .h
        f"/Fp{paths['gen_pre_pch']}",                   # Use Precompiled .pch
        f"/Fd{paths['gen_pdb']}",                       # Database File
        f"/Fo{buildfile}",                              # Object File
    ]
    file_path = f"{file}"
    _ppch= [f"{paths['compiler']}",*commonCompileOptions,*extraOptions,file_path]
    print(*_ppch,sep=" ")
    print()
    compile_pch = run(_ppch,capture_output=False,cwd=f"{paths['source']}")
    return compile_pch.returncode

def link(paths:Dict[str,WindowsPath]):
    print("\nLinking to .exe")
    link_args =[
        "/ERRORREPORT:PROMPT",
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
    obj_main = f"{paths['gen_main']}"
    obj_ppch = f"{paths['gen_pch']}"
    _args= [f"{paths['linker']}",*link_args,obj_main,obj_ppch,f"{paths['gen_util']}"]
    print(*_args,sep=" ")
    print()
    run_linker = run(_args,capture_output=False,cwd=f"{paths['source']}")
    return run_linker.returncode

#
# Script Only for Build
#
if __name__ == "__main__":

    print("Build Command:",*sys.argv[1:])

    # Only work in windows
    if  sys.platform != "win32":
        exit(1)

    # Project Directories
    source_directory = WindowsPath(__file__).parent.parent
    build_directory = source_directory.joinpath("./build/")

    # Compiler and Linker
    vc_path = os.getenv("VCToolsInstallDir")
    if vc_path is None:
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
    check_res = check_paths(project_paths)
    if check_res == False:
        exit(1)
    print("",*project_paths.values(),sep="\n\t")

    # Hash
    with open(project_paths["main.cpp"],mode="r",encoding="utf8") as fp:
        print(hashlib.sha1(fp.read().encode(encoding="utf8")).hexdigest())

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
            #if _c1 == 0 and sys.argv.__len__() == 3:
            #    if  re.match(r"^link$",sys.argv[2],flags=re.IGNORECASE) is not None:
            #        link(project_paths)
        # Link only
        if  re.match(r"^link$",sys.argv[1],flags=re.IGNORECASE) is not None:
            link(project_paths)
