#include "devices.h"
#include <algorithm>
#include <stdexcept>
#include <cmath>

LightDevice::LightDevice(const std::string& id, const std::string& name,int brightness,double maxPower,bool on,bool critical, const std::string& priority)
        : DeviceBase(id, name, on, critical),
            brightness(brightness),
            maxPower(maxPower)
{
        setPriority(priority);
}

DeviceType LightDevice::getType() const
{
    return DeviceType::Light;
}

double LightDevice::getCurrentPower() const
{
    if (!on)
        return 0.0;

    double b = std::clamp(brightness, 0, 100);
    return maxPower * (b / 100.0);
}

void LightDevice::setBrightness(int value)
{
    brightness = std::clamp(value, 0, 100);
}

int LightDevice::getBrightness() const
{
    return brightness;
}

void LightDevice::updateFromJson(const json& j)
{
    if (j.contains("is_on"))
        on = j["is_on"].get<bool>();

    if (j.contains("brightness"))
        setBrightness(j["brightness"].get<int>());
    if (j.contains("priority"))
        setPriority(j["priority"].get<std::string>());
}

json LightDevice::toJson(const std::string& roomName) const
{
    json j = baseJson(roomName);
    j["type"] = "light";
    j["brightness"] = brightness;
    j["max_power"] = maxPower;
    j["current_power"] = getCurrentPower();
    return j;
}

ClimateDevice::ClimateDevice(const std::string& id, const std::string& name, int targetTemperature, double basePower, bool on, bool critical, const std::string& priority)
        : DeviceBase(id, name, on, critical),
            targetTemperature(targetTemperature),
            basePower(basePower)
{
        setPriority(priority);
}

DeviceType ClimateDevice::getType() const
{
    return DeviceType::Climate;
}

double ClimateDevice::getCurrentPower() const
{
    if (!on)
        return 0.0;

    int diff = std::abs(targetTemperature - 22);
    double factor = 1.0 + diff * 0.03;
    return basePower * factor;
}

int ClimateDevice::getTargetTemperature() const
{
    return targetTemperature;
}

void ClimateDevice::setTargetTemperature(int t)
{
    targetTemperature = t;
}

void ClimateDevice::updateFromJson(const json& j)
{
    if (j.contains("is_on"))
        on = j["is_on"].get<bool>();

    if (j.contains("target_temperature"))
        targetTemperature = j["target_temperature"].get<int>();
    if (j.contains("priority"))
        setPriority(j["priority"].get<std::string>());
}

json ClimateDevice::toJson(const std::string& roomName) const
{
    json j = baseJson(roomName);
    j["type"] = "climate";
    j["target_temperature"] = targetTemperature;
    j["base_power"] = basePower;
    j["current_power"] = getCurrentPower();
    return j;
}

SmartPlugDevice::SmartPlugDevice(const std::string& id, const std::string& name, double loadPower, bool on, bool critical, const std::string& priority)
        : DeviceBase(id, name, on, critical),
            loadPower(loadPower)
{
        setPriority(priority);
}

DeviceType SmartPlugDevice::getType() const
{
    return DeviceType::SmartPlug;
}

double SmartPlugDevice::getCurrentPower() const
{
    if (!on)
        return 0.0;
    return loadPower;
}

double SmartPlugDevice::getLoadPower() const
{
    return loadPower;
}

void SmartPlugDevice::setLoadPower(double p)
{
    loadPower = std::max(0.0, p);
}

void SmartPlugDevice::updateFromJson(const json& j)
{
    if (j.contains("is_on"))
        on = j["is_on"].get<bool>();

    if (j.contains("load_power"))
        setLoadPower(j["load_power"].get<double>());
    if (j.contains("priority"))
        setPriority(j["priority"].get<std::string>());
}

json SmartPlugDevice::toJson(const std::string& roomName) const
{
    json j = baseJson(roomName);
    j["type"] = "smart_plug";
    j["load_power"] = loadPower;
    j["current_power"] = getCurrentPower();
    return j;
}


std::unique_ptr<IDevice> DeviceFactory::create(DeviceType type, const std::string& id, const std::string& name)
{
    switch (type)
    {
    case DeviceType::Light:
        return std::make_unique<LightDevice>(id, name);
    case DeviceType::Climate:
        return std::make_unique<ClimateDevice>(id, name);
    case DeviceType::SmartPlug:
        return std::make_unique<SmartPlugDevice>(id, name);
    default:
        throw std::runtime_error("Unknown device type in DeviceFactory::create(name)");
    }
}

std::unique_ptr<IDevice> DeviceFactory::create(DeviceType type,const std::string& id,const json& config)
{
    std::string name = config.value("name", id);

    switch (type)
    {
    case DeviceType::Light:
    {
        int brightness = config.value("brightness", 100);
        double maxP = config.value("max_power", 60.0);
        bool on = config.value("is_on", true);
        bool crit = config.value("critical", false);
        std::string pr = config.value("priority", std::string("medium"));
        return std::make_unique<LightDevice>(id, name, brightness, maxP, on, crit, pr);
    }
    case DeviceType::Climate:
    {
        int t = config.value("target_temperature", 22);
        double base = config.value("base_power", 1000.0);
        bool on = config.value("is_on", true);
        bool crit = config.value("critical", true);
        std::string pr = config.value("priority", std::string("medium"));
        return std::make_unique<ClimateDevice>(id, name, t, base, on, crit, pr);
    }
    case DeviceType::SmartPlug:
    {
        double load = config.value("load_power", 200.0);
        bool on = config.value("is_on", true);
        bool crit = config.value("critical", false);
        std::string pr = config.value("priority", std::string("medium"));
        return std::make_unique<SmartPlugDevice>(id, name, load, on, crit, pr);
    }
    default:
        throw std::runtime_error("Unknown device type in DeviceFactory::create(config)");
    }
}

DeviceType deviceTypeFromString(const std::string& typeStr)
{
    if (typeStr == "light")
        return DeviceType::Light;
    if (typeStr == "climate")
        return DeviceType::Climate;
    if (typeStr == "smart_plug")
        return DeviceType::SmartPlug;

    throw std::runtime_error("Unknown device type string: " + typeStr);
}
