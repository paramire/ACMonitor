import mosquitto
mqttc = mosquitto.Mosquitto("python_pub")
mqttc.will_set("/event/dropped", "Sorry, I seem to have died.")
mqttc.connect("10.200.114.193", 1883, 60, True)

mqttc.publish("outTopic", "PythonClient") 