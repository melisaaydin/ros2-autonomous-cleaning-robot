import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('ev_robot_description')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')

    #map file path
    map_file = os.path.join(os.path.expanduser('~'), 'ros2_ws/src/ev_robot_description/maps/kusursuz_harita.yaml')

    # 1. Simülasyonu Başlatma
    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_share, 'launch', 'sim.launch.py'))
    )
    # 2. Navigasyonu Başlatma
    nav_launch = TimerAction(
        period=5.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(os.path.join(nav2_bringup_dir, 'launch', 'bringup_launch.py')),
                launch_arguments={
                    'use_sim_time': 'True',
                    'autostart': 'True',
                    'map': map_file
                }.items()
            )
        ]
    )
    #ROSbridge- web bağlantısı başlatma
    rosbridge_cmd = ExecuteProcess(
        cmd=['ros2', 'launch', 'rosbridge_server', 'rosbridge_websocket_launch.xml'],
        output='screen'
    )
    # Python dosyasının tam yolunu veriyoruz - AppControl
    app_kontrol_script = os.path.join(os.path.expanduser('~'), 'ros2_ws/src/ev_robot_description/ev_robot_description/app_kontrol.py')
    app_kontrol_node = ExecuteProcess(
        cmd=['python3', app_kontrol_script],
        output='screen'
    )
    # 5. RViz'i Başlat 
    rviz_cmd = ExecuteProcess(
        cmd=['ros2', 'run', 'rviz2', 'rviz2', '-d', os.path.join(nav2_bringup_dir, 'rviz', 'nav2_default_view.rviz')],
        output='screen'
    )
    return LaunchDescription([
        sim_launch,
        nav_launch,
        rosbridge_cmd,
        app_kontrol_node,
        rviz_cmd 
    ])
