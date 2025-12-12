#include "consumption_history.h"
#include <algorithm>
#include <ctime>
#include <iomanip>
#include <sstream>

ConsumptionHistory::ConsumptionHistory()
{
}

std::string ConsumptionHistory::getCurrentTimestamp() const
{
    auto now = std::chrono::system_clock::now();
    std::time_t time = std::chrono::system_clock::to_time_t(now);
    std::stringstream ss;
    ss << std::put_time(std::gmtime(&time), "%Y-%m-%dT%H:%M:%SZ");
    return ss.str();
}

void ConsumptionHistory::recordConsumption(double power_watt, double price_per_kwh)
{
    ConsumptionEntry entry;
    entry.timestamp = getCurrentTimestamp();
    entry.total_power = power_watt;
    entry.total_cost = (power_watt / 1000.0) * price_per_kwh;

    entries.push_back(entry);
    pruneOldEntries();
}

bool ConsumptionHistory::isWithinTimeRange(const std::string& timestamp, int minutes) const
{
    auto now = std::chrono::system_clock::now();
    std::time_t now_time = std::chrono::system_clock::to_time_t(now);

    std::tm tm = {};
    sscanf(timestamp.c_str(), "%d-%d-%dT%d:%d:%dZ",
           &tm.tm_year, &tm.tm_mon, &tm.tm_mday,
           &tm.tm_hour, &tm.tm_min, &tm.tm_sec);

    tm.tm_year -= 1900;
    tm.tm_mon -= 1;

    std::time_t entry_time = mktime(&tm);

    double diff_seconds = difftime(now_time, entry_time);
    return diff_seconds <= (minutes * 60);
}

std::vector<ConsumptionEntry> ConsumptionHistory::getLastMinutes(int minutes) const
{
    std::vector<ConsumptionEntry> result;
    for (const auto& entry : entries)
    {
        if (isWithinTimeRange(entry.timestamp, minutes))
        {
            result.push_back(entry);
        }
    }
    return result;
}

std::vector<ConsumptionEntry> ConsumptionHistory::getLastHours(int hours) const
{
    return getLastMinutes(hours * 60);
}

std::vector<ConsumptionEntry> ConsumptionHistory::getLastDays(int days) const
{
    return getLastMinutes(days * 24 * 60);
}

double ConsumptionHistory::getAverageConsumption() const
{
    if (entries.empty())
        return 0.0;

    double sum = 0.0;
    for (const auto& entry : entries)
    {
        sum += entry.total_power;
    }
    return sum / entries.size();
}

json ConsumptionHistory::toJson() const
{
    json result = json::array();
    for (const auto& entry : entries)
    {
        json j;
        j["timestamp"] = entry.timestamp;
        j["power"] = entry.total_power;
        j["cost"] = entry.total_cost;
        result.push_back(j);
    }
    return result;
}

void ConsumptionHistory::fromJson(const json& j)
{
    entries.clear();
    if (!j.is_array())
        return;

    for (const auto& item : j)
    {
        ConsumptionEntry entry;
        entry.timestamp = item.value("timestamp", "");
        entry.total_power = item.value("power", 0.0);
        entry.total_cost = item.value("cost", 0.0);
        entries.push_back(entry);
    }
}

void ConsumptionHistory::pruneOldEntries()
{
    if (entries.size() > MAX_ENTRIES)
    {
        entries.erase(entries.begin(), entries.end() - MAX_ENTRIES);
    }
}

void ConsumptionHistory::clear()
{
    entries.clear();
}

size_t ConsumptionHistory::size() const
{
    return entries.size();
}
