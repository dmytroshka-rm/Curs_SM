cmake_minimum_required(VERSION 3.10)
project(SmartHomeBackend)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(smart_home_server
    main.cpp
    src/devices.cpp
    src/logger.cpp
    src/smart_home.cpp
    src/strategy.cpp
    src/consumption_history.cpp
    src/schedule.cpp
)

target_include_directories(smart_home_server PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/crow
    ${CMAKE_CURRENT_SOURCE_DIR}/asio
)

if (MSVC)
    target_compile_definitions(smart_home_server PRIVATE _WIN32_WINNT=0x0601)
    target_compile_options(smart_home_server PRIVATE /W3)
endif()

find_package(Threads REQUIRED)
target_link_libraries(smart_home_server PRIVATE Threads::Threads)

if (WIN32)
    target_link_libraries(smart_home_server PRIVATE ws2_32)
endif()
