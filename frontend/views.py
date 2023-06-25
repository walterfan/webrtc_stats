from flask import Flask, render_template
from . import app, logger
from .forms import ToolForm, UploadForm

ALLOWED_EXTENSIONS = set(['txt', 'log', 'json'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/tool')
def tool():
    upload_form = UploadForm()
    tool_form = ToolForm()
    return render_template('tool.html', form=tool_form, upload_form=upload_form)

@app.route('/upload', methods=['POST'])
def upload_stats():
    upload_form = UploadForm()
    tool_form = ToolForm()
    input_content = ""
    if upload_form.validate_on_submit():
        file = upload_form.script_file.data
        logger.info('filename={}'.format(file.filename))
        if file and allowed_file(file.filename):

            file_content = file.read()
            if file_content:
                input_content = file_content.decode('UTF-8').strip()
                tool_form.input_content.data = input_content
            file.close()

            logger.info('File successfully uploaded: {}'.format(input_content))
    else:
        logger.info(upload_form.errors)



    return render_template('index.html', form=tool_form, upload_form=upload_form)
