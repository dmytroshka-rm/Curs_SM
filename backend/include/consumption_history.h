#pragma once

#include <vector>
#include <string>
#include <chrono>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

struct ConsumptionEntry
{
    std::string timestamp;
    double total_power;
    double total_cost;
};

class ConsumptionHistory
{
public:
    ConsumptionHistory();

    void recordConsumption(double power_watt, double price_per_kwh = 0.0);

    std::vector<ConsumptionEntry> getLastMinutes(int minutes) const;

    std::vector<ConsumptionEntry> getLastHours(int hours) const;

    std::vector<ConsumptionEntry> getLastDays(int days) const;

    double getAverageConsumption() const;

    json toJson() const;

    void fromJson(const json& j);

    void clear();

    size_t size() const;

private:
    std::vector<ConsumptionEntry> entries;
    static constexpr size_t MAX_ENTRIES = 10080;

    std::string getCurrentTimestamp() const;
    bool isWithinTimeRange(const std::string& timestamp, int minutes) const;
    void pruneOldEntries();
};
