import mosquitto
mqttc = mosquitto.Mosquitto("python_pub")
mqttc.will_set("/event/dropped", "Sorry, I seem to have died.")
mqttc.connect("127.0.0.1", 1883, 60, True)

mqttc.publish("hello/world", "PythonClient") 