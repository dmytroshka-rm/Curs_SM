#pragma once

#include <vector>
#include <memory>
#include <string>
#include <optional>
#include <functional>
#include <nlohmann/json.hpp>
#include "devices.h"
#include "strategy.h"

using json = nlohmann::json;

class Room
{
private:
    std::string id;
    std::string name;
    std::vector<std::unique_ptr<IDevice>> devices;

public:
    Room(std::string id, std::string name);

    const std::string& getId() const;
    const std::string& getName() const;

    void setName(const std::string& newName);

    IDevice* addDevice(std::unique_ptr<IDevice> dev);

    const std::vector<std::unique_ptr<IDevice>>& getDevices() const;

    bool removeDeviceById(const std::string& deviceId);

    std::vector<IDevice*> getDevicesRaw();

    double totalPower() const;

    json toJson() const;
};

class SmartHome
{
private:
    std::vector<Room> rooms;
    std::unique_ptr<IEnergyOptimizationStrategy> strategy;

    int nextRoomId = 1;
    int nextDeviceId = 1;
    std::vector<double> optimization_history;
    std::string state_file = "smarthome_state.json";

public:
    SmartHome();

    Room& addRoom(const std::string& name);
    void deleteRoom(const std::string& roomId);
    std::optional<std::reference_wrapper<Room>> findRoomById(const std::string& id);
    const std::vector<Room>& getRooms() const;

    IDevice* addDeviceToRoom(const std::string& roomId,DeviceType type,const json& config);

    void deleteDevice(const std::string& deviceId);

    std::optional<IDevice*> findDeviceById(const std::string& id);


    json getAllDevicesJson() const;

    json getRoomsJson() const;
    json getStatsJson() const;

    json updateDeviceState(const std::string& deviceId, const json& newState);

    json optimize(int tariffLevel);

private:
    std::string generateRoomId();
    std::string generateDeviceId();
    void saveState() const;
    void loadState();
};
