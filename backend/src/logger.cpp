#include "logger.h"
#include <chrono>
#include <iomanip>
#include <ctime>

Logger& Logger::instance()
{
    static Logger inst;
    return inst;
}

Logger::Logger()
{
    ofs.open("smarthome.log", std::ios::app);
}

Logger::~Logger()
{
    if (ofs.is_open())
        ofs.close();
}

void Logger::write(const std::string& level, const std::string& msg)
{
    std::lock_guard<std::mutex> lock(mtx);
    if (!ofs.is_open()) return;

    auto now = std::chrono::system_clock::now();
    std::time_t t = std::chrono::system_clock::to_time_t(now);
    ofs << std::put_time(std::localtime(&t), "%Y-%m-%d %H:%M:%S") << " [" << level << "] " << msg << "\n";
    ofs.flush();
}

void Logger::info(const std::string& msg)
{
    write("INFO", msg);
}

void Logger::warn(const std::string& msg)
{
    write("WARN", msg);
}

void Logger::error(const std::string& msg)
{
    write("ERROR", msg);
}
