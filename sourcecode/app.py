from flask import Flask, render_template, request, make_response, session
from processing import process

# /Users/zeyadzaki/Desktop/Fall19/DD2/MiniProject/uart.def
# /Users/zeyadzaki/Desktop/Fall19/DD2/MiniProject/osu035_stdcells.lef

app = Flask(__name__)
app.secret_key = 'dev'


@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        def_file = request.form["def_file_path"]
        lef_file = request.form["lef_file_path"]
        drc_file = request.form["drc_file_path"]
        cell_types, cell_names, pin_names, net_names = process(def_file, lef_file, drc_file)
        return render_template('layout.html', cell_types=cell_types, cell_names=cell_names, pin_names=pin_names,
                               net_names=net_names)
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
