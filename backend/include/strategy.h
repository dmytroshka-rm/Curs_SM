#pragma once

#include <memory>
#include <vector>
#include <string>
#include <nlohmann/json.hpp>
#include "devices.h"

using json = nlohmann::json;

class Room;

class IEnergyOptimizationStrategy
{
public:
    virtual ~IEnergyOptimizationStrategy() = default;

    virtual void optimize(std::vector<Room>& rooms, int tariffLevel) = 0;
};

class BasicTariffOptimizationStrategy : public IEnergyOptimizationStrategy
{
public:
    void optimize(std::vector<Room>& rooms, int tariffLevel) override;
};
