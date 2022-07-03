import project

from subprocess import run
import os, pathlib, sys, re, string

def prepareEnv():

    if sys.platform.__eq__("win32") == False:
        print("Only win32 development platform permited!")
        exit(1)

    vc_tools = os.getenv("VCToolsInstallDir")
    if vc_tools == None:
        print("Visual Studio Tools Env[VCToolsInstallDir] not found!")
        exit(1)

    vc_tools_directory = pathlib.WindowsPath(vc_tools)
    if vc_tools_directory.exists() == False:
        print("Visual Studio Tools Path not found!")
        exit(1)

    vc_compiler_directory = vc_tools_directory.joinpath("./bin/HostX64/x64")
    if vc_compiler_directory.exists() == False:
        print("Compiler path not found!")
        exit(1)

    vc_compiler = vc_compiler_directory.joinpath("./cl.exe")
    vc_linker = vc_compiler_directory.joinpath("./link.exe")

    if vc_compiler.exists() == False:
        print("Compiler not found!")
        exit(1)

    if vc_linker.exists() == False:
        print("Linker not found!")
        exit(1)

    exec_directory = pathlib.WindowsPath(os.getcwd())
    script_directory = pathlib.WindowsPath(__file__)
    source_directory = script_directory.parent.parent
    build_directory = source_directory.joinpath("./build/")

    print(f"Building from [{exec_directory}]")
    print(f"Script [{script_directory.name}] Path: [{script_directory}]")
    print(f"Build Directory [{build_directory}]")
    print(f"Source Root Directory [{source_directory}]")
    print(f"Compiler [{vc_compiler}]")
    print(f"Linker [{vc_linker}]\n")
    return [source_directory,build_directory,vc_compiler,vc_linker]

def clean(path:pathlib.WindowsPath):
    print(f"Clean directory: [{path}]")
    files_to_clean = os.listdir(path)
    files_removed = 0
    for i in files_to_clean:
        _file = path.joinpath(i)
        print(f"\tRemoving file [{_file}]")
        try:
            os.remove(_file)
            files_removed+=1
        except OSError as err:
            print(f"\tError [{err.strerror}] trying to remove [{_file}]")
    print(f"Files Removed: {files_removed}")

def precompile(proj:project.W32Master):
    print("Precompiling")
    _ppch = proj.precompiled_pch()
    compile_pch = run([proj.compiler_path.__str__(),*_ppch],capture_output=False,cwd=proj.build_path.__str__())
    return compile_pch.returncode

def compile(proj:project.W32Master):
    print("Compiling")
    _ppch = proj.compiled_main()
    compile_pch = run([proj.compiler_path.__str__(),*_ppch],capture_output=False,cwd=proj.build_path.__str__())
    return compile_pch.returncode

def link(proj:project.W32Master):
    print("Link main.exe")
    _link_flags = proj.linke_exe()
    _link = run([proj.linker_path.__str__(),*_link_flags],capture_output=False,cwd=proj.build_path.__str__())
    return _link.returncode


if __name__ == "__main__":
    _src,_build,_cp,_lp = prepareEnv()

    _proj = project.W32Master(_build,_src,_cp,_lp)

    if sys.argv.__len__() > 1:
        if  re.match(r"^clean$",sys.argv[1],flags=re.IGNORECASE) is not None:
            clean(_build)
        if  re.match(r"^precompile$",sys.argv[1],flags=re.IGNORECASE) is not None:
            print(precompile(_proj))
        if  re.match(r"^compile$",sys.argv[1],flags=re.IGNORECASE) is not None:
            _c1 =compile(_proj)
            if _c1 == 0 and sys.argv.__len__() == 3:
                if  re.match(r"^link$",sys.argv[2],flags=re.IGNORECASE) is not None:
                    link(_proj)
