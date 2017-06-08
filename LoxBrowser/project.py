from flask import Flask, request , render_template
from Bio.Seq import Seq
from Bio.Alphabet import generic_dna

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("input.html")

@app.route('/output', methods=['POST'])
def output():
        

    return render_template("output.html", output=output)

@app.route('/output2', methods=['POST'])
def output2():
    

    return render_template("output.html", output=output)




if __name__ == '__main__':
    app.run(debug=True)