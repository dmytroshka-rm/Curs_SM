#include "strategy.h"
#include "smart_home.h"
#include <algorithm>
#include <iostream>

static void softReduceDevice(IDevice* dev)
{
    if (!dev)
        return;

    switch (dev->getType())
    {
    case DeviceType::Light:
    {
        auto* light = dynamic_cast<LightDevice*>(dev);
        if (light && light->isOn())
        {
            int b = light->getBrightness();
            light->setBrightness(std::max(10, b - 30)); 
        }
        break;
    }
    case DeviceType::Climate:
    {
        auto* cl = dynamic_cast<ClimateDevice*>(dev);
        if (cl && cl->isOn())
        {
            int t = cl->getTargetTemperature();
            if (t > 22) cl->setTargetTemperature(t - 1);
            else if (t < 22) cl->setTargetTemperature(t + 1);
        }
        break;
    }
    case DeviceType::SmartPlug:
    {
        auto* sp = dynamic_cast<SmartPlugDevice*>(dev);
        if (sp && sp->isOn())
        {
            double load = sp->getLoadPower();
            sp->setLoadPower(load * 0.8);
        }
        break;
    }
    }
}

void BasicTariffOptimizationStrategy::optimize(std::vector<Room>& rooms, int tariffLevel)
{
    if (tariffLevel == 0)
        return;

    struct DevRef
    {
        Room* room;
        IDevice* device;
    };

    std::vector<DevRef> allDevices;
    size_t total_devices = 0;
    for (const auto& r : rooms)
        total_devices += r.getDevices().size();
    allDevices.reserve(total_devices);
    
    for (auto& r : rooms)
    {
        for (auto* d : r.getDevicesRaw())
        {
            if (d)
                allDevices.push_back({ &r, d });
        }
    }

    double totalPower = 0.0;
    for (const auto& ref : allDevices)
        totalPower += ref.device->getCurrentPower();

    if (tariffLevel == 1)
    {
        for (auto& ref : allDevices)
        {
            softReduceDevice(ref.device);
        }
        return;
    }

    if (tariffLevel >= 2)
    {
        std::sort(allDevices.begin(), allDevices.end(), [](const DevRef& a, const DevRef& b) {
            return a.device->getCurrentPower() > b.device->getCurrentPower();
        });

        for (auto& ref : allDevices)
        {
            if (ref.device->isCritical())
                continue;

            if (!ref.device->isOn())
                continue;

            double before = ref.device->getCurrentPower();
            ref.device->setOn(false);

            totalPower -= before;

            if (totalPower < 500.0)
                break;
        }
    }
}
