from flask import Flask, render_template, request, send_file
import pandas as pd
from pathlib import Path
from FlaskApp import costs2
#from scalingPolicy import scalingPolicy
from FlaskApp import Predictor2

app = Flask(__name__)

base_dir = str(Path().resolve())

names = ['Conf', 'profile', 'Cuser', 'rate', 'RT', 'KO', 'Nrequest', '%KO', 'RTStdDev']
#ConfTable=['1WPmedium_1DBlarge ']
ConfTable=['1WPmedium_1DBmedium ','3WPmedium_1DBmedium ','1WPmedium_1DBlarge ','2WPmedium_1DBlarge ','3WPmedium_1DBlarge ']#,'1WPlarge_1DB ']
#ConfTable=['1WPmedium_1DBmedium ','2WPmedium_1DBmedium ','3WPmedium_1DBmedium ']
#CostTable={'medium':0.0288,'large':0.0576,'xlarge':0.1152,'xxlarge':0.2304,'':0.2304}
CostTable={'medium':0.0576,'large':0.1152,'xlarge':0.2304,'xxlarge':0.2304,'':0.2304}

Profiles=[' author ',' editor ',' shopmanager ', ' userreader ']
MixtureProfiles = [' mixturea ',' mixtureb ']
Mixtures=[[0.25,0.25,0.25,0.25],[0.1,0.2,0.2,0.5]]
#Profiles=[' userreader ']

file = base_dir + '/dataset/stats.csv'
df = pd.read_csv(file, names=names, header=None)
costs = costs2.costs2(CostTable)
predictor = Predictor2.Predictor2(df, ConfTable, Profiles, Mixtures, MixtureProfiles, costs)

#mix=0
#predictor.predict(mix)

@app.route("/", methods=['GET', 'POST'])
def main():

    return render_template('index0.html')

@app.route("/tipo")
def tipo():

    return render_template('index.html')

@app.route("/measur")
def measur():

    return render_template('index2.html')
@app.route("/err")
def e():
    return render_template('index3.html')
@app.route("/pred")
def p():
    return render_template('index4.html')
#@app.route("/all")
#def all():
#    return render_template('imgPlotAll.html')
#@app.route("/all.png")
#def a():
#    img1 = predictor.plotCTRL('KO', 'measured')
#    img2 = predictor.plotCTRL('KO','predicted')
#    img3 = predictor.plotCTRL('KO','error')

#    img4 = predictor.plotCTRL('RT','measured')
#    img5 = predictor.plotCTRL('RT','predicted')
#    img6 = predictor.plotCTRL('RT','error')
#    img7 = predictor.plotCTRL('Rate','measured')
#    img8 = predictor.plotCTRL('Rate','predicted')
#    img9 = predictor.plotCTRL('Rate','error')
#    return send_file(img1, img2, img3, img4, img5, img6, img7, img8, img9, mimetype='image/png', cache_timeout=0)

@app.route("/process", methods = ["GET", "POST"])
def process_form():

    mix = int(request.form['options'])
    predictor.predict(mix)
    print(mix)

    return render_template('index.html', mix = mix)


@app.route("/measured/<var>")
def measured(var):
    return render_template('img.html', var =var)

@app.route("/measured<var>.png")
def measuredplot(var):
    img = predictor.plotCTRL(var,'measured')
    return send_file(img, mimetype='image/png', cache_timeout=0)

@app.route("/measured/MAR")
def measuredMAR():
    return render_template('measuredMAR.html')
@app.route("/measuredMAR.png")
def mMAR():
    img = predictor.plot_MAR(MixtureProfiles[predictor.MixID],'measured')
    return send_file(img, mimetype='image/png', cache_timeout=0)

@app.route("/predicred/<var>")
def predicted(var):
    return render_template('img2.html', var =var)

@app.route("/predicted<var>.png")
def predictedplot(var):
    img = predictor.plotCTRL(var,'predicted')
    return send_file(img, mimetype='image/png', cache_timeout=0)

@app.route("/predicted/MAR")
def predictedMAR():
    return render_template('predictedMAR.html')
@app.route("/predictedMAR.png")
def pMAR():
    img = predictor.plot_MAR(MixtureProfiles[predictor.MixID],'predicted')
    return send_file(img, mimetype='image/png', cache_timeout=0)

@app.route("/error/<var>")
def error(var):
    return render_template('img3.html', var =var)

@app.route("/error<var>.png")
def errorplot(var):
    img = predictor.plotCTRL(var,'error')
    return send_file(img, mimetype='image/png', cache_timeout=0)


if __name__ == "__main__":
    app.run()


########option = request.form['options'] ####per mixture