#ifndef SCHEDULE_H
#define SCHEDULE_H

#include <string>
#include <vector>
#include <map>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

struct ScheduleEntry {
    std::string device_id;
    int day_of_week;
    bool enabled;
    int turn_on_hour;
    int turn_on_minute;
    int turn_off_hour;
    int turn_off_minute;

    json toJson() const;
    static ScheduleEntry fromJson(const json& j);
};

class Schedule {
public:
    Schedule();

    void addEntry(const ScheduleEntry& entry);

    void removeEntry(const std::string& device_id, int day_of_week);

    std::vector<ScheduleEntry> getDeviceSchedules(const std::string& device_id) const;

    std::vector<ScheduleEntry> getAllSchedules() const;

    std::pair<std::vector<std::string>, std::vector<std::string>> getActionsForCurrentTime() const;

    json toJson() const;
    void fromJson(const json& j);

private:
    std::map<std::string, std::map<int, ScheduleEntry>> schedules;

    int getCurrentDayOfWeek() const;

    std::pair<int, int> getCurrentTime() const;

    bool isTimeInRange(int start_hour, int start_minute, 
                      int end_hour, int end_minute) const;
};

#endif
