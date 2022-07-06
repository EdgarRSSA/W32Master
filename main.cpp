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


/**
 * @brief Entry Main.
 *
 * @return int Exit code.
 */
int main()
{
    auto mega = "";
    std::cout << "Win32/C++" << std::endl;
    std::cout << "Pruebas de API" << std::endl;

    Chang chang{1};
    auto res = CheckChang(chang);

    typedef DWORD PID;
    PID processid = GetCurrentProcessId();
    std::cout << "PID: " << processid << std::endl;
    return ERROR_SUCCESS;
}
