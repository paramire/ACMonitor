from flask import Flask, render_template, jsonify
from datetime import datetime
app = Flask(__name__)


#Nuestra Pagina Responsable de indicar si debemos correr en circulos o no
@app.route("/", defaults={'w':None})
@app.route("/<w>")
def index(w):
	if w is None:
		w_h = True
	else:
		w_h = False

	return render_template('index.html', warning_h = w_h)

#Funcion Responsable de obtener una actualizacion desde Arduino/RaspberryPi
#Debemos obtener los datos desde la Raspberry las 

@app.route("/status")
def status():
	#Contectarme a Raspberry_Pi o Arduino
	#Code
	
	#MySQL con los Estados

	#JSON
	#temp_rp = request.args.get('a',0,type=int)
	#state_rp = request.args.get('b',0,type=int)
	temp_rp =  75
	state_rp = "off"
	return jsonify(temp = temp_rp,state = state_rp)

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0',threaded=True)