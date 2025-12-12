#pragma once

#include <string>
#include <memory>
#include <vector>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

enum class DeviceType
{
    Light,
    Climate,
    SmartPlug
};

class IDevice
{
public:
    virtual ~IDevice() = default;

    virtual std::string getId() const = 0;
    virtual std::string getName() const = 0;
    virtual DeviceType getType() const = 0;

    virtual double getCurrentPower() const = 0;   
    virtual bool isCritical() const = 0;          

    virtual bool isOn() const = 0;
    virtual void setOn(bool on) = 0;

    virtual void updateFromJson(const json& j) = 0;

    virtual json toJson(const std::string& roomName) const = 0;
};

class DeviceBase : public IDevice
{
protected:
    std::string id;
    std::string name;
    bool on;
    bool critical;
    std::string priority;

public:
    DeviceBase(std::string id, std::string name, bool on = true, bool critical = false)
        : id(std::move(id)), name(std::move(name)), on(on), critical(critical)
    {
    }

    std::string getPriority() const { return priority; }
    void setPriority(const std::string& p) { priority = p; }

    std::string getId() const override { return id; }
    std::string getName() const override { return name; }

    bool isOn() const override { return on; }
    void setOn(bool value) override { on = value; }

    bool isCritical() const override { return critical; }

    json baseJson(const std::string& roomName) const
    {
        json j;
        j["id"] = id;
        j["name"] = name;
        j["is_on"] = on;
        j["critical"] = critical;
        j["room"] = roomName;
        j["priority"] = priority;
        return j;
    }
};


class LightDevice : public DeviceBase
{
private:
    int brightness;      
    double maxPower;    

public:
    LightDevice(const std::string& id,const std::string& name, int brightness = 100,double maxPower = 60.0,bool on = true,bool critical = false, const std::string& priority = "medium");

    DeviceType getType() const override;

    double getCurrentPower() const override;

    void setBrightness(int value);
    int getBrightness() const;

    void updateFromJson(const json& j) override;

    json toJson(const std::string& roomName) const override;
};


class ClimateDevice : public DeviceBase
{
private:
    int targetTemperature;  
    double basePower;       

public:
    ClimateDevice(const std::string& id,const std::string& name,int targetTemperature = 22,double basePower = 1000.0,bool on = true,bool critical = true, const std::string& priority = "medium");

    DeviceType getType() const override;

    double getCurrentPower() const override;

    int getTargetTemperature() const;
    void setTargetTemperature(int t);

    void updateFromJson(const json& j) override;

    json toJson(const std::string& roomName) const override;
};


class SmartPlugDevice : public DeviceBase
{
private:
    double loadPower;   

public:
    SmartPlugDevice(const std::string& id,const std::string& name,double loadPower = 200.0,bool on = true,bool critical = false, const std::string& priority = "medium");

    DeviceType getType() const override;

    double getCurrentPower() const override;

    double getLoadPower() const;
    void setLoadPower(double p);

    void updateFromJson(const json& j) override;

    json toJson(const std::string& roomName) const override;
};

class DeviceFactory
{
public:
    static std::unique_ptr<IDevice> create(DeviceType type,const std::string& id,const std::string& name);

    static std::unique_ptr<IDevice> create(DeviceType type,const std::string& id,const json& config);
};

DeviceType deviceTypeFromString(const std::string& typeStr);
