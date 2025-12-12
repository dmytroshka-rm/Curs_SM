#include "crow/app.h"
#include "smart_home.h"
#include "consumption_history.h"
#include "schedule.h"
#include <nlohmann/json.hpp>
#include <iostream>
#include <thread>
#include <chrono>
#include <fstream>
using json = nlohmann::json;

void saveSchedulesToFile(const Schedule& schedule, const std::string& filename = "schedules.json") {
    try {
        std::ofstream file(filename);
        file << schedule.toJson().dump(2);
        file.close();
    } catch (const std::exception& ex) {
        std::cout << "Error saving schedules: " << ex.what() << std::endl;
    }
}

void loadSchedulesFromFile(Schedule& schedule, const std::string& filename = "schedules.json") {
    try {
        std::ifstream file(filename);
        if (file.good()) {
            json j;
            file >> j;
            schedule.fromJson(j);
            std::cout << "Schedules loaded from file" << std::endl;
        }
    } catch (const std::exception& ex) {
        std::cout << "Error loading schedules: " << ex.what() << std::endl;
    }
}

int main()
{
    crow::SimpleApp app;
    SmartHome home;
    ConsumptionHistory consumption_history;
    Schedule schedule;
    
    loadSchedulesFromFile(schedule);

    CROW_ROUTE(app, "/devices").methods(crow::HTTPMethod::GET)(
        [&]() {
            try {
                return crow::response(home.getAllDevicesJson().dump());
            }
            catch (const std::exception& ex) {
                return crow::response(500, json{{"status","error"},{"message",ex.what()}}.dump());
            }
        });

    CROW_ROUTE(app, "/rooms").methods(crow::HTTPMethod::GET)(
        [&]() {
            try {
                return crow::response(home.getRoomsJson().dump());
            }
            catch (const std::exception& ex) {
                return crow::response(500, json{{"status","error"},{"message",ex.what()}}.dump());
            }
        });

    CROW_ROUTE(app, "/device/update").methods(crow::HTTPMethod::POST)(
        [&](const crow::request& req) {
            try {
                json body = json::parse(req.body);
                std::string id = body.value("id", "");
                json state = body.value("state", json::object());

                if (id.empty())
                    return crow::response(400, R"({"status":"error","message":"Device id missing"})");

                return crow::response(home.updateDeviceState(id, state).dump());
            }
            catch (const std::exception& ex) {
                return crow::response(400, json{{"status","error"},{"message",ex.what()}}.dump());
            }
        });

    CROW_ROUTE(app, "/optimize").methods(crow::HTTPMethod::POST)(
        [&](const crow::request& req) {
            try {
                json body = json::parse(req.body);
                int tariff = body.value("tariff", 1);
                return crow::response(home.optimize(tariff).dump());
            }
            catch (const std::exception& ex) {
                return crow::response(400, json{{"status","error"},{"message",ex.what()}}.dump());
            }
        });

    CROW_ROUTE(app, "/rooms/add").methods(crow::HTTPMethod::POST)(
        [&](const crow::request& req) {
            try {
                json body = json::parse(req.body);
                std::string name = body.value("name", "");

                if (name.empty())
                    return crow::response(400, R"({"status":"error","message":"Room name missing"})");

                Room& room = home.addRoom(name);

                json resp;
                resp["status"] = "ok";
                resp["room"] = room.toJson();
                return crow::response(resp.dump());
            }
            catch (const std::exception& ex) {
                return crow::response(400, json{{"status","error"},{"message",ex.what()}}.dump());
            }
        });

    CROW_ROUTE(app, "/devices/add").methods(crow::HTTPMethod::POST)(
        [&](const crow::request& req) {
            try {
                json body = json::parse(req.body);

                std::string roomId = body.value("room_id", "");
                std::string typeStr = body.value("type", "");
                json config = body.value("config", json::object());

                if (roomId.empty() || typeStr.empty())
                    return crow::response(400, R"({"status":"error","message":"Missing room_id or type"})");

                DeviceType type;
                if (typeStr == "light") type = DeviceType::Light;
                else if (typeStr == "climate") type = DeviceType::Climate;
                else if (typeStr == "smart_plug") type = DeviceType::SmartPlug;
                else
                    return crow::response(400, R"({"status":"error","message":"Unknown device type"})");

                IDevice* dev = home.addDeviceToRoom(roomId, type, config);

                std::string roomName;
                for (const auto& r : home.getRooms())
                    if (r.getId() == roomId) roomName = r.getName();

                json resp;
                resp["status"] = "ok";
                resp["room_id"] = roomId;
                resp["device"] = dev->toJson(roomName);
                return crow::response(resp.dump());
            }
            catch (const std::exception& ex) {
                return crow::response(400, json{{"status","error"},{"message",ex.what()}}.dump());
            }
        });

    CROW_ROUTE(app, "/devices/delete").methods(crow::HTTPMethod::POST)(
        [&](const crow::request& req) {
            try {
                json body = json::parse(req.body);
                std::string id = body.value("device_id", "");

                if (id.empty())
                    return crow::response(400, R"({"status":"error","message":"Device id missing"})");

                home.deleteDevice(id);

                return crow::response(json{{"status","ok"}}.dump());
            }
            catch (const std::exception& ex) {
                return crow::response(400, json{{"status","error"},{"message",ex.what()}}.dump());
            }
        });

    CROW_ROUTE(app, "/rooms/delete").methods(crow::HTTPMethod::POST)(
        [&](const crow::request& req) {
            try {
                json body = json::parse(req.body);
                std::string id = body.value("room_id", "");

                if (id.empty())
                    return crow::response(400, R"({"status":"error","message":"Room id missing"})");

                home.deleteRoom(id);

                return crow::response(json{{"status","ok"}}.dump());
            }
            catch (const std::exception& ex) {
                return crow::response(400, json{{"status","error"},{"message",ex.what()}}.dump());
            }
        });

    CROW_ROUTE(app, "/stats").methods(crow::HTTPMethod::GET)(
        [&]() {
            try {
                double total_power = 0.0;
                for (const auto& r : home.getRooms())
                    total_power += r.totalPower();
                consumption_history.recordConsumption(total_power);

                return crow::response(home.getStatsJson().dump());
            }
            catch (const std::exception& ex) {
                return crow::response(500, json{{"status","error"},{"message",ex.what()}}.dump());
            }
        });

    CROW_ROUTE(app, "/chart/history").methods(crow::HTTPMethod::GET)([&](const crow::request& req) {
        try {
            auto period = req.url_params.get("period");
            std::string period_str = period ? std::string(period) : "24hours";

            std::vector<ConsumptionEntry> data;
            if (period_str == "1hour")
                data = consumption_history.getLastHours(1);
            else if (period_str == "24hours")
                data = consumption_history.getLastHours(24);
            else if (period_str == "7days")
                data = consumption_history.getLastDays(7);
            else
                data = consumption_history.getLastHours(24);

            json result;
            result["period"] = period_str;
            result["average"] = consumption_history.getAverageConsumption();
            result["data"] = json::array();

            for (const auto& entry : data)
            {
                json j;
                j["timestamp"] = entry.timestamp;
                j["power"] = entry.total_power;
                j["cost"] = entry.total_cost;
                result["data"].push_back(j);
            }

            return crow::response(result.dump());
        }
        catch (const std::exception& ex) {
            return crow::response(400, json{{"status","error"},{"message",ex.what()}}.dump());
        }
    });

    CROW_ROUTE(app, "/schedules/<string>").methods(crow::HTTPMethod::GET)(
        [&](const std::string& device_id) {
            try {
                auto schedules = schedule.getDeviceSchedules(device_id);
                json result = json::array();
                for (const auto& entry : schedules) {
                    result.push_back(entry.toJson());
                }
                return crow::response(result.dump());
            }
            catch (const std::exception& ex) {
                return crow::response(400, json{{"status","error"},{"message",ex.what()}}.dump());
            }
        });

    CROW_ROUTE(app, "/schedules/save").methods(crow::HTTPMethod::POST)(
        [&](const crow::request& req) {
            try {
                json body = json::parse(req.body);
                ScheduleEntry entry = ScheduleEntry::fromJson(body);
                schedule.addEntry(entry);
                saveSchedulesToFile(schedule);
                std::cout << "Schedule saved for device " << entry.device_id << " day " << entry.day_of_week << std::endl;
                return crow::response(json{{"status","ok"},{"message","Schedule saved"}}.dump());
            }
            catch (const std::exception& ex) {
                return crow::response(400, json{{"status","error"},{"message",ex.what()}}.dump());
            }
        });

    CROW_ROUTE(app, "/schedules/delete").methods(crow::HTTPMethod::POST)(
        [&](const crow::request& req) {
            try {
                json body = json::parse(req.body);
                std::string device_id = body["device_id"];
                int day_of_week = body["day_of_week"];
                schedule.removeEntry(device_id, day_of_week);
                saveSchedulesToFile(schedule);
                std::cout << "Schedule deleted for device " << device_id << " day " << day_of_week << std::endl;
                return crow::response(json{{"status","ok"},{"message","Schedule deleted"}}.dump());
            }
            catch (const std::exception& ex) {
                return crow::response(400, json{{"status","error"},{"message",ex.what()}}.dump());
            }
        });

    std::thread scheduler_thread([&]() {
        while (true) {
            try {
                std::this_thread::sleep_for(std::chrono::seconds(60));
                
                std::pair<std::vector<std::string>, std::vector<std::string>> actions = 
                    schedule.getActionsForCurrentTime();
                std::vector<std::string> turn_on_devices = actions.first;
                std::vector<std::string> turn_off_devices = actions.second;
                
                for (const auto& device_id : turn_on_devices) {
                    json state;
                    state["power"] = true;
                    home.updateDeviceState(device_id, state);
                    std::cout << "Schedule: Turned on device " << device_id << std::endl;
                }
                
                for (const auto& device_id : turn_off_devices) {
                    json state;
                    state["power"] = false;
                    home.updateDeviceState(device_id, state);
                    std::cout << "Schedule: Turned off device " << device_id << std::endl;
                }
            }
            catch (const std::exception& ex) {
                std::cout << "Scheduler error: " << ex.what() << std::endl;
            }
        }
    });
    scheduler_thread.detach();

    std::cout << "Server running: http://localhost:8080" << std::endl;
    app.port(8080).multithreaded().run();
}
