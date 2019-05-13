# Pet Home Companion

This the the project submission for **Pet Home Companion**. If you want to learn about Pet Home Companion, you can go the our website [Pet Home Companion](https://iotcolumbia2019glzz.weebly.com/) or [Github Page](https://github.com/guoshanglin/Smart-Pet-Care). 

# Files

The files in this submission are organized under four directories: Lambda, ML, MQTT, and Website.

* The **Lambda** directory contains two lamdba funtions that are depolyed on AWS Lambda Funtions service. 
* The **ML** directory contains the machin learning components of this project, including Google Vision Kit and scanner_for_ML script
	* The **Google Vision Kit** subdirectory contains the code that is deployed on the  [Google Vision Kit](https://aiyprojects.withgoogle.com/vision/) that detects the presence of pets in real-time.
	* The **scanner_for_ML** script is used when measuring the RSSI value at various distance, which is eventually used as the data input of linear regression algorithm.
* The **MQTT** directory contains the script that are deployed on three Raspberry Pi scanning stations that evertually publish the data via MQTT to [AWS IoT Platform](https://aws.amazon.com/iot-core/). 
	* The **MQTT_PI_1.py** script running on the master node not only publishes the distance data, but also collects the weight data and controls the sevo when instructed.
* The **Website** directory contains the web application that are implemented using Node.js. 

