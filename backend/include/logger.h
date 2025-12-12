#pragma once

#include <string>
#include <fstream>
#include <mutex>
#include <memory>

class Logger
{
public:
    static Logger& instance();

    void info(const std::string& msg);
    void warn(const std::string& msg);
    void error(const std::string& msg);

private:
    Logger();
    ~Logger();

    void write(const std::string& level, const std::string& msg);

    std::ofstream ofs;
    std::mutex mtx;
};
