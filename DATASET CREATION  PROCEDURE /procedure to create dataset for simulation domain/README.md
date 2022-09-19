refer this link to install ros melodic.  https://wiki.ros.org/melodic/Installation/Ubuntu
and the  loading the world with camera is refered from https://sir.upc.edu/projects/rostutorials/9-gazebo_sensors_tutorial/index.html#depth-label.



to add all the models to the path
export GAZEBO_MODEL_PATH=~/catkin_ws/src/gazebo_sensors_tutorial/models/:${GAZEBO_MODEL_PATH}


#to source all the files:

source ~/.bashrc

#sourcing ros melodic

source /opt/ros/melodic/setup.bash

#creating catkin workspace

#creating to workspace

 cd catkin_ws
 
$ mkdir -p ~/catkin_ws/src

$ cd ~/catkin_ws/

$ catkin_make
 

#move the gazebo_sensor tutorial to the src file of the catkin workspace

#sourcing the workspace

 source devel/setup.bash

#launching the world with camera(bright light conditions)

roslaunch gazebo_sensors_tutorial kinect_diffuse.launch 

#normal light:

roslaunch gazebo_sensors_tutorial kinect_normal.launch 

#low light:

roslaunch gazebo_sensors_tutorial kinect_emmissive.launch 

#in other terminal:

 roslaunch gazebo_sensors_tutorial kinect_coke_rviz.launch

#to download the images from the rgbd camera:

rosrun rqt_image_view rqt_image_view 
    
    

    


 


            
 
