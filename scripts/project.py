from pathlib import WindowsPath

class W32Master:

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

    def __init__(self, build:WindowsPath, source:WindowsPath, compiler:WindowsPath, linker:WindowsPath):
        self.build_path = build
        self.source_path = source
        self.compiler_path = compiler
        self.linker_path = linker

    def precompiled_pch(self):
        file_name = "pch"
        extraOptions = [
            f"/Yc{file_name}.h",                                # Create Precompiled
            f"/Fp{self.build_path.joinpath(file_name+'.pch')}", # Precompiled File
            f"/Fd{self.build_path.joinpath('main.pdb')}",       # Database File
            f"/Fo{self.build_path.joinpath(file_name+'.obj')}", # Object File
        ]
        file_path = self.source_path.joinpath(file_name+'.cpp').__str__()
        return [*self.commonCompileOptions,*extraOptions,file_path]

    def compiled_main(self):
        file_name = "main"
        precompiled_file = "pch"
        extraOptions = [
            f"/Yu{precompiled_file}.h",                                # Use Precompiled .h
            f"/Fp{self.build_path.joinpath(precompiled_file+'.pch')}", # Use Precompiled .pch
            f"/Fd{self.build_path.joinpath('main.pdb')}", # Database File
            f"/Fo{self.build_path}\\",                                 # Object File
        ]
        file_path = self.source_path.joinpath(file_name+'.cpp').__str__()
        return [*self.commonCompileOptions,*extraOptions,file_path]

    def linke_exe(self):
        ccc =[ "/ERRORREPORT:PROMPT",
            f"/OUT:{self.build_path.joinpath('app.exe')}",
            "/INCREMENTAL",
            f"/ILK:{self.build_path.joinpath('main.ilk')}",
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
            f"/PDB:{self.build_path.joinpath('main.pdb')}",
            "/SUBSYSTEM:CONSOLE",
            "/TLBID:1",
            "/DYNAMICBASE",
            "/NXCOMPAT",
            f"/IMPLIB:{self.build_path.joinpath('main.lib')}",
            "/MACHINE:X64",
        ]
        obj_main = self.build_path.joinpath('main'+'.obj').__str__()
        obj_ppch = self.build_path.joinpath('pch'+'.obj').__str__()
        return [*ccc,obj_main,obj_ppch]
