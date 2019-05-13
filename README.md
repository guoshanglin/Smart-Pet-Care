# Smart Pet Care

This is project **Smart Pet Care**. If you want to learn about Smart Pet Care, you can go to our website [Smart Pet Care](https://iotcolumbia2019glzz.weebly.com/) or [Github Page](https://github.com/guoshanglin/Smart-Pet-Care). 

# Files

The files in this submission are organized under four directories: Lambda, ML, MQTT, and Website.

* The **Lambda** directory contains two lambda functions that are deployed on AWS Lambda Functions service. 
* The **ML** directory contains the machine learning components of this project, including Google Vision Kit and scanner_for_ML script
	* The **Google Vision Kit** subdirectory contains the code that is deployed on the  [Google Vision Kit](https://aiyprojects.withgoogle.com/vision/) that detects the presence of pets in real-time.
	* The **scanner_for_ML** script is used when measuring the RSSI value at various distances, which is eventually used as the data input of a linear regression algorithm.
* The **MQTT** directory contains the scripts that are deployed on three Raspberry Pi scanning stations that evertually publish the data via MQTT to [AWS IoT Platform](https://aws.amazon.com/iot-core/). 
	* The **MQTT_PI_1.py** script running on the master node not only publishes the distance data, but also collects the weight data and controls the servo when instructed.
* The **Website** directory contains the web application that is implemented using Node.js. 
