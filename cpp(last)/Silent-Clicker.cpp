#include <iostream>
#include <windows.h>
#include <conio.h>
#include <ctime>
#include <cstdlib>
#include <string>

const int MIN_INTERVAL = 17;
const int MAX_INTERVAL = 50;
const int MAX_CPS_LEFT = 21;


void setConsoleColor(int textColor, int bgColor) {
    SetConsoleTextAttribute(GetStdHandle(STD_OUTPUT_HANDLE), (bgColor << 4) | textColor);
}


void leftClick() {
    HWND hwnd = GetForegroundWindow();

    SendMessage(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, MAKELPARAM(0, 0));


    int clickInterval = static_cast<int>(1000.0 / MAX_CPS_LEFT);
    Sleep(clickInterval);

    SendMessage(hwnd, WM_LBUTTONUP, 0, MAKELPARAM(0, 0));
}
void rightClick() {
    HWND hwnd = GetForegroundWindow();

    SendMessage(hwnd, WM_RBUTTONDOWN, MK_RBUTTON, MAKELONG(0, 0));


    int clickInterval = MIN_INTERVAL + rand() % (MAX_INTERVAL - MIN_INTERVAL);
    Sleep(clickInterval);


    SendMessage(hwnd, WM_RBUTTONUP, MK_RBUTTON, MAKELONG(0, 0));
}

int main() {

    setConsoleColor(15, 0);

    std::cout << "=============================\n";
    std::cout << "  Welcome to Slient Clicker  \n";
    std::cout << "=============================\n";
    
    std::cout << "Enter the new program name: ";
    std::string newProgramName;
    std::getline(std::cin, newProgramName);
    system(("title " + newProgramName).c_str());

    std::cout << "Press any key to start...\n";
    _getch();

    // 初始化随机数种子
    srand(static_cast<unsigned int>(time(nullptr)));

    HWND hwnd = GetConsoleWindow();
    ShowWindow(hwnd, SW_HIDE);

    bool leftClickEnabled = true;
    bool rightClickEnabled = true;

    std::cout << "\nControls:\n";
    std::cout << "  'L' - Toggle Left Click\n";
    std::cout << "  'R' - Toggle Right Click\n";
    std::cout << "  'Esc' - Exit\n";
    std::cout << "=============================\n";

    while (true) {

        if (GetAsyncKeyState('L') & 0x8000) {
            leftClickEnabled = !leftClickEnabled;
            std::cout << "Left Click " << (leftClickEnabled ? "Enabled" : "Disabled") << "\n";
            Sleep(500); // 防止快速切换
        }

        if (GetAsyncKeyState('R') & 0x8000) {
            rightClickEnabled = !rightClickEnabled;
            std::cout << "Right Click " << (rightClickEnabled ? "Enabled" : "Disabled") << "\n";
            Sleep(500); // 防止快速切换
        }


        if (GetAsyncKeyState(VK_ESCAPE)) {
            break;
        }


        if (rightClickEnabled && GetAsyncKeyState(VK_RBUTTON)) {
            rightClick();
        }


        if (leftClickEnabled && GetAsyncKeyState(VK_XBUTTON2)) {
            leftClick();
        }

        Sleep(10);
    }

    return 0;
}
