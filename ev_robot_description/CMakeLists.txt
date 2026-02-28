cmake_minimum_required(VERSION 3.8)
project(ev_robot_description)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)

# Klasörleri yükle (Scripts artık burada olmayacak)
install(DIRECTORY
  urdf
  config
  launch
  worlds
  DESTINATION share/${PROJECT_NAME}
)

# Python dosyasını ÇALIŞTIRILABİLİR olarak yükle (Asıl çözüm burası)
install(PROGRAMS
  scripts/supurge_beyni.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()