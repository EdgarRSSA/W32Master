#include "pch.h"

/**
 * @brief Entry Main.
 *
 * @return int Exit code.
 */
int main()
{
    std::cout << "Hello Win32/C++ console" << std::endl;

    typedef DWORD PID;
    PID _count = GetCurrentProcessId();
    std::cout << "PID: " << _count << std::endl;
    return ERROR_SUCCESS;
}
