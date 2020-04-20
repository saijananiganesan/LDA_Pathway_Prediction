from flask import Flask, flash, render_template, request, url_for, redirect
import jinja2
import os

app = Flask(__name__)

templateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=templateLoader)
template_html = "template.html"
Template_Dict={}

def add(num1,num2):
    num3=float(num1)+float(num2)
    return num3

def write_html(Template_Dict, template_file):
    template = templateEnv.get_template(template_file)
    outputText=template.render(Template_Dict)
    with open(os.path.join(dirName,template_file),"w") as fh:
        fh.write(outputText)
        
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/application/")
def application():
    return render_template("application.html")

@app.route('/form/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        name=request.form['Name']
        email=request.form['Email']
        if name and email:
            return redirect(url_for('application'))
        else:
            return "<h1>Please fill your details to proceed.</h1>"

    return render_template('form.html')


@app.route('/form-example', methods=['GET', 'POST']) #allow both GET and POST requests
def form_example():
    if request.method == 'POST':  #this block is only entered when the form is submitted
        num1 = request.form.get('num1')
        num2 = request.form['num2']
        num3=add(num1,num2)
        return render_template("template2.html",num1=num1,num2=num2,num3=num3)
    return '''<form method="POST">
                  FIRST Num: <input type="float" name="num1"><br>
                  Second Num: <input type="float" name="num2"><br>
                  <input type="submit" value="Submit"><br>
              </form>'''

if __name__ == "__main__":
    app.run(debug=True)