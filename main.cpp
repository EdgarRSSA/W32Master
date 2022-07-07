/**
 * @file main.cpp
 * @author Edgar Rosales
 * @brief Console Main.
 * @version 0.1
 * @date 2022-07-05
 *
 * @copyright Copyright (c) 2022
 *
 */

// PRECOMPILED
#include "utils.h"
#include "pch.h"
// NOT PRECOMPILED


namespace CarbonFileIO
{
    using std::filesystem::path;
    typedef std::vector<std::filesystem::path> Pathlist;

    HANDLE openfile(const path file)
    {
        if (file.empty()) return 0;

        DWORD file_type = 0;
        auto res = GetBinaryTypeW(file.c_str(), &file_type);
        if (res!=0)
        {
            std::cout << "Error, file is in executable format" << std::endl;
            return 0;
        }

        auto file_handle = CreateFileW(file.c_str(), GENERIC_READ, 0, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_READONLY, NULL);
        if(file_handle == (HANDLE)ERROR_FILE_NOT_FOUND)
        {
            std::cout << "Not file found" << std::endl;
            return 0;
        }

        if  (file_handle == INVALID_HANDLE_VALUE)
        {
            std::cout << "Invalid File" << std::endl;
            return 0;
        }

        res = GetFileType(file_handle);
        if (res==FILE_TYPE_DISK)
        {
            return file_handle;
        }

        CloseHandle(file_handle);
        std::cout << "Invalid Type of File" << std::endl;

        return 0;
    }

    Pathlist GetPathList(const path directory){
        Pathlist path_list{};
        WIN32_FIND_DATAW find_data{};
        auto find_file = FindFirstFileW(directory.c_str(), &find_data);
        bool find_loop = find_file != 0;
        BOOL findnext_file{};
        std::wstring find_file_name{};
        while (find_loop)
        {
            find_file_name = find_data.cFileName;
            path_list.push_back(path{directory.parent_path()} /= find_file_name);
            findnext_file = FindNextFileW(find_file, &find_data);
            if (findnext_file == 0){
                find_loop = false;
                auto find_empty = GetLastError() == ERROR_NO_MORE_FILES;
                if (find_empty)
                {
                    std::cout << "No more files" << std::endl;
                }
                else
                {
                    std::cout << "Error when iterate" << std::endl;
                }
                FindClose(find_file);
            }
        }
        return path_list;
    }

}

/**
 * @brief Entry Main.
 *
 * @return int Exit code.
 */
int main(const int argc,const char* argv[])
{
    constexpr int APP_ERROR = 1;
    constexpr int APP_SUCCESS = 0;

    if (argc == 1)
    {
        std::cout << "Error, Need a file name." << std::endl;
        return APP_ERROR;
    }

    std::filesystem::path file_path{(char *)argv[1]};

    //auto list = std::move(CarbonFileIO::GetPathList(file_path));
    auto list = CarbonFileIO::GetPathList(file_path);
    std::cout << std::format("{}:", file_path.string()) << std::endl;
    for (auto &i: list)
    {
        std::cout << std::format("{}", i.string()) << std::endl;
    }

    //auto file_handle = CarbonFileIO::openfile(file_path);
    //if (file_handle == 0)
    //{
    //    return APP_ERROR;
    //}
    //
    //std::cout << std::format("Opened, file is {}", file_path.string()) << std::endl;
    //
    //CloseHandle(file_handle);
    //std::cout << "File Closed" << std::endl;

    return APP_SUCCESS;
}
