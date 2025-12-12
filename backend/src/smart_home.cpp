#include "smart_home.h"
#include <algorithm>
#include <stdexcept>
#include <fstream>
#include "logger.h"

Room::Room(std::string id, std::string name)
    : id(std::move(id)), name(std::move(name))
{
}

const std::string& Room::getId() const
{
    return id;
}

const std::string& Room::getName() const
{
    return name;
}

void Room::setName(const std::string& newName)
{
    name = newName;
}

IDevice* Room::addDevice(std::unique_ptr<IDevice> dev)
{
    if (!dev)
        return nullptr;

    IDevice* raw = dev.get();
    devices.push_back(std::move(dev));
    return raw;
}

const std::vector<std::unique_ptr<IDevice>>& Room::getDevices() const
{
    return devices;
}

bool Room::removeDeviceById(const std::string& deviceId)
{
    auto it = std::find_if(devices.begin(), devices.end(),
        [&deviceId](const std::unique_ptr<IDevice>& d) { return d && d->getId() == deviceId; });

    if (it != devices.end())
    {
        devices.erase(it);
        return true;
    }
    return false;
}

std::vector<IDevice*> Room::getDevicesRaw()
{
    std::vector<IDevice*> res;
    res.reserve(devices.size());
    for (auto& d : devices)
        res.push_back(d.get());
    return res;
}

double Room::totalPower() const
{
    double sum = 0.0;
    for (const auto& d : devices)
        sum += d->getCurrentPower();
    return sum;
}

json Room::toJson() const
{
    json j;
    j["id"] = id;
    j["name"] = name;
    j["total_power"] = totalPower();

    json devs = json::array();
    for (const auto& d : devices)
    {
        devs.push_back(d->toJson(name));
    }
    j["devices"] = devs;

    return j;
}


SmartHome::SmartHome()
{
    strategy = std::make_unique<BasicTariffOptimizationStrategy>();
    try {
        loadState();
        Logger::instance().info("State loaded on startup");
    } catch (const std::exception& ex) {
        Logger::instance().warn(std::string("No state loaded: ") + ex.what());
    }
}

Room& SmartHome::addRoom(const std::string& name)
{
    std::string id = generateRoomId();
    rooms.emplace_back(id, name);
    saveState();
    Logger::instance().info(std::string("Added room: ") + name + " id=" + id);
    return rooms.back();
}

void SmartHome::deleteRoom(const std::string& roomId)
{
    auto it = std::find_if(rooms.begin(), rooms.end(),
        [&roomId](const Room& r) { return r.getId() == roomId; });
    
    if (it == rooms.end())
        throw std::runtime_error("Room not found: " + roomId);
    
    rooms.erase(it);
    saveState();
    Logger::instance().info(std::string("Deleted room: ") + roomId);
}

std::optional<std::reference_wrapper<Room>> SmartHome::findRoomById(const std::string& id)
{
    for (auto& r : rooms)
    {
        if (r.getId() == id)
            return r;
    }
    return std::nullopt;
}

const std::vector<Room>& SmartHome::getRooms() const
{
    return rooms;
}

IDevice* SmartHome::addDeviceToRoom(const std::string& roomId, DeviceType type, const json& config)
{
    auto roomOpt = findRoomById(roomId);
    if (!roomOpt.has_value())
        throw std::runtime_error("Room not found: " + roomId);

    Room& room = roomOpt.value();

    std::string devId = generateDeviceId();

    auto dev = DeviceFactory::create(type, devId, config);
    IDevice* raw = room.addDevice(std::move(dev));
    saveState();
    Logger::instance().info(std::string("Added device id=") + devId);
    return raw;
}

void SmartHome::deleteDevice(const std::string& deviceId)
{
    for (auto& r : rooms)
    {
        if (r.removeDeviceById(deviceId))
        {
            saveState();
            Logger::instance().info(std::string("Deleted device id=") + deviceId);
            return;
        }
    }

    throw std::runtime_error("Device not found: " + deviceId);
}

std::optional<IDevice*> SmartHome::findDeviceById(const std::string& id)
{
    for (auto& r : rooms)
    {
        auto devices = r.getDevicesRaw();
        for (auto* d : devices)
        {
            if (d && d->getId() == id)
                return d;
        }
    }
    return std::nullopt;
}

json SmartHome::getAllDevicesJson() const
{
    json arr = json::array();
    
    for (const auto& r : rooms)
    {
        for (const auto& d : r.getDevices())
        {
            if (d)
                arr.push_back(d->toJson(r.getName()));
        }
    }
    return arr;
}

json SmartHome::getRoomsJson() const
{
    json arr = json::array();
    for (const auto& r : rooms)
    {
        arr.push_back(r.toJson());
    }
    return arr;
}

json SmartHome::updateDeviceState(const std::string& deviceId, const json& newState)
{
    auto devOpt = findDeviceById(deviceId);
    if (!devOpt.has_value())
    {
        json err;
        err["status"] = "error";
        err["message"] = "Device not found";
        return err;
    }

    IDevice* dev = devOpt.value();
    dev->updateFromJson(newState);

    std::string roomName = "unknown";
    for (const auto& r : rooms)
    {
        for (const auto& d : r.getDevices())
        {
            if (d && d->getId() == deviceId)
            {
                roomName = r.getName();
                break;
            }
        }
        if (roomName != "unknown")
            break;
    }

    json resp;
    resp["status"] = "ok";
    resp["device"] = dev->toJson(roomName);
    saveState();
    Logger::instance().info(std::string("Updated device state: ") + deviceId);
    return resp;
}

json SmartHome::optimize(int tariffLevel)
{
    if (strategy)
    {
        strategy->optimize(rooms, tariffLevel);
    }

    double total = 0.0;
    for (const auto& r : rooms)
        total += r.totalPower();

    optimization_history.push_back(total);
    if (optimization_history.size() > 20)
        optimization_history.erase(optimization_history.begin(), optimization_history.end() - 20);

    saveState();
    Logger::instance().info(std::string("Optimization run: tariff=") + std::to_string(tariffLevel) + std::string(" total=") + std::to_string(total));

    json result;
    result["status"] = "ok";
    result["tariff"] = tariffLevel;
    result["rooms"] = getRoomsJson();
    result["devices"] = getAllDevicesJson();
    return result;
}

std::string SmartHome::generateRoomId()
{
    return "room_" + std::to_string(nextRoomId++);
}

std::string SmartHome::generateDeviceId()
{
    return "dev_" + std::to_string(nextDeviceId++);
}

void SmartHome::saveState() const
{
    try {
        json j;
        j["nextRoomId"] = nextRoomId;
        j["nextDeviceId"] = nextDeviceId;
        j["rooms"] = getRoomsJson();
        j["optimization_history"] = optimization_history;

        std::ofstream ofs(state_file);
        if (!ofs)
            throw std::runtime_error("Cannot open state file for writing");
        ofs << j.dump(4);
        ofs.close();
    } catch (const std::exception& ex) {
        Logger::instance().error(std::string("Failed to save state: ") + ex.what());
    }
}

void SmartHome::loadState()
{
    std::ifstream ifs(state_file);
    if (!ifs)
        throw std::runtime_error("State file not found");

    json j;
    ifs >> j;

    if (j.contains("nextRoomId")) nextRoomId = j["nextRoomId"].get<int>();
    if (j.contains("nextDeviceId")) nextDeviceId = j["nextDeviceId"].get<int>();

    if (j.contains("optimization_history"))
        optimization_history = j["optimization_history"].get<std::vector<double>>();

    rooms.clear();
    if (j.contains("rooms")) {
        for (const auto& rj : j["rooms"]) {
            std::string rid = rj.value("id", std::string(""));
            std::string rname = rj.value("name", std::string(""));
            rooms.emplace_back(rid, rname);
            Room& room = rooms.back();

            if (rj.contains("devices")) {
                for (const auto& dj : rj["devices"]) {
                    std::string typeStr = dj.value("type", std::string("light"));
                    DeviceType dt = deviceTypeFromString(typeStr);
                    std::string did = dj.value("id", std::string(""));
                    auto dev = DeviceFactory::create(dt, did, dj);
                    room.addDevice(std::move(dev));
                }
            }
        }
    }
}

json SmartHome::getStatsJson() const
{
    json j;
    double total = 0.0;
    json roomsArr = json::array();

    for (const auto& r : rooms) {
        double rp = r.totalPower();
        total += rp;
        json rj;
        rj["id"] = r.getId();
        rj["name"] = r.getName();
        rj["total_power"] = rp;

        char rating = 'D';
        if (rp < 100) rating = 'A';
        else if (rp < 300) rating = 'B';
        else if (rp < 800) rating = 'C';
        rj["rating"] = std::string(1, rating);

        json devs = json::array();
        for (const auto& up : r.getDevices()) {
            if (up)
                devs.push_back(up->toJson(r.getName()));
        }
        rj["devices"] = devs;
        roomsArr.push_back(rj);
    }

    j["total_power"] = total;
    j["rooms"] = roomsArr;
    j["optimization_history"] = optimization_history;

    int m = std::min<size_t>(5, optimization_history.size());
    double forecast = 0.0;
    if (m > 0) {
        for (size_t i = optimization_history.size() - m; i < optimization_history.size(); ++i)
            forecast += optimization_history[i];
        forecast /= m;
    }
    j["forecast_next_total"] = forecast;

    return j;
}
