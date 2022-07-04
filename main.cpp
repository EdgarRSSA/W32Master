#include "pch.h"

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

    typedef DWORD PID;
    PID _count = GetCurrentProcessId();
    std::cout << "PID: " << _count << std::endl;
    return ERROR_SUCCESS;
}
