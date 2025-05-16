cmake_minimum_required(VERSION 3.10)
project(pcl_clipper)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add the executable
add_executable(clip main.cpp)

# Add warnings for safety
target_compile_options(clip PRIVATE -Wall -Wextra -Wpedantic)

install(TARGETS clip DESTINATION install)
install(PROGRAMS visualize.py DESTINATION install)

# Optional: enable optimization for release builds
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()
