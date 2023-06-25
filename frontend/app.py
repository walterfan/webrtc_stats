from flask import Flask, render_template
from . import app, logger
from .forms import ToolForm, UploadForm
from . import views
import os

dir_path = os.path.dirname(os.path.realpath(__file__))


@app.route('/')
def index():
    upload_form = UploadForm()
    tool_form = ToolForm()
    return render_template('index.html', form=tool_form, upload_form=upload_form)

@app.route('/test')
def test():
    tool_form = ToolForm()
    return render_template('test.html', form=tool_form)



