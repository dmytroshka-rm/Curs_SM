#include "../include/schedule.h"
#include <ctime>
#include <algorithm>

json ScheduleEntry::toJson() const {
    json j;
    j["device_id"] = device_id;
    j["day_of_week"] = day_of_week;
    j["enabled"] = enabled;
    j["turn_on_hour"] = turn_on_hour;
    j["turn_on_minute"] = turn_on_minute;
    j["turn_off_hour"] = turn_off_hour;
    j["turn_off_minute"] = turn_off_minute;
    return j;
}

ScheduleEntry ScheduleEntry::fromJson(const json& j) {
    ScheduleEntry entry;
    entry.device_id = j["device_id"];
    entry.day_of_week = j["day_of_week"];
    entry.enabled = j["enabled"];
    entry.turn_on_hour = j["turn_on_hour"];
    entry.turn_on_minute = j["turn_on_minute"];
    entry.turn_off_hour = j["turn_off_hour"];
    entry.turn_off_minute = j["turn_off_minute"];
    return entry;
}

Schedule::Schedule() {
}

void Schedule::addEntry(const ScheduleEntry& entry) {
    schedules[entry.device_id][entry.day_of_week] = entry;
}

void Schedule::removeEntry(const std::string& device_id, int day_of_week) {
    if (schedules.find(device_id) != schedules.end()) {
        schedules[device_id].erase(day_of_week);
        if (schedules[device_id].empty()) {
            schedules.erase(device_id);
        }
    }
}

std::vector<ScheduleEntry> Schedule::getDeviceSchedules(const std::string& device_id) const {
    std::vector<ScheduleEntry> result;
    auto it = schedules.find(device_id);
    if (it != schedules.end()) {
        for (const auto& pair : it->second) {
            result.push_back(pair.second);
        }
    }
    return result;
}

std::vector<ScheduleEntry> Schedule::getAllSchedules() const {
    std::vector<ScheduleEntry> result;
    for (const auto& device_pair : schedules) {
        for (const auto& day_pair : device_pair.second) {
            result.push_back(day_pair.second);
        }
    }
    return result;
}

int Schedule::getCurrentDayOfWeek() const {
    time_t now = time(nullptr);
    struct tm* timeinfo = localtime(&now);
    int wday = timeinfo->tm_wday;
    return (wday + 6) % 7;  
}

std::pair<int, int> Schedule::getCurrentTime() const {
    time_t now = time(nullptr);
    struct tm* timeinfo = localtime(&now);
    return std::make_pair(timeinfo->tm_hour, timeinfo->tm_min);
}

bool Schedule::isTimeInRange(int start_hour, int start_minute,
                            int end_hour, int end_minute) const {
    auto [current_hour, current_minute] = getCurrentTime();
    int current_total = current_hour * 60 + current_minute;
    int start_total = start_hour * 60 + start_minute;
    int end_total = end_hour * 60 + end_minute;

    if (start_total <= end_total) {
        return current_total >= start_total && current_total < end_total;
    } else {
        return current_total >= start_total || current_total < end_total;
    }
}

std::pair<std::vector<std::string>, std::vector<std::string>> 
Schedule::getActionsForCurrentTime() const {
    std::vector<std::string> turn_on_devices;
    std::vector<std::string> turn_off_devices;

    int current_day = getCurrentDayOfWeek();
    auto [current_hour, current_minute] = getCurrentTime();

    for (const auto& device_pair : schedules) {
        const std::string& device_id = device_pair.first;
        const auto& day_schedules = device_pair.second;

        auto it = day_schedules.find(current_day);
        if (it != day_schedules.end()) {
            const ScheduleEntry& entry = it->second;
            if (!entry.enabled) continue;

            if (current_hour == entry.turn_on_hour && 
                current_minute == entry.turn_on_minute) {
                turn_on_devices.push_back(device_id);
            }

            if (current_hour == entry.turn_off_hour && 
                current_minute == entry.turn_off_minute) {
                turn_off_devices.push_back(device_id);
            }
        }
    }

    return std::make_pair(turn_on_devices, turn_off_devices);
}

json Schedule::toJson() const {
    json schedules_array = json::array();
    for (const auto& entry : getAllSchedules()) {
        schedules_array.push_back(entry.toJson());
    }
    return schedules_array;
}

void Schedule::fromJson(const json& j) {
    schedules.clear();
    if (j.is_array()) {
        for (const auto& item : j) {
            ScheduleEntry entry = ScheduleEntry::fromJson(item);
            addEntry(entry);
        }
    }
}
