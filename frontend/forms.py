from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, PasswordField
from wtforms import BooleanField, SelectField, FileField
from wtforms import HiddenField
from wtforms.validators import DataRequired, Length, Optional
import datetime

WEBRT_STATS_TYPES = [
    "inbound-rtp",
    "outbound-rtp",
    "remote-inbound-rtp" ,
    "remote-outbound-rtp",
    "transceiver" ,
    "sender",
    "receiver" ,
    "transport" ,
    "candidate-pair" ,
    "stream" ,
    "track" ,
    "codec" ,
    "media-source",
    "csrc",
    "peer-connection",
    "local-candidate",
    "remote-candidate",
    "certificate",
    "ice-server",
    "data-channel",
    "sctp-transport"
]

def get_stats_type_choices():
    choices = []
    for stats_type in WEBRT_STATS_TYPES:
        choices.append((stats_type, stats_type))
    return choices

class UploadForm(FlaskForm):
    script_file = FileField('Upload Script', validators=[FileAllowed(['txt'])])
    submit_file = SubmitField('Upload')

class ToolForm(FlaskForm):

    input_content = TextAreaField('input', validators=[DataRequired(), Length(1, 8192)],
                                   render_kw={
                                       "class": "form-control",
                                       "rows": 10})
    output_content = TextAreaField('output', validators=[DataRequired(), Length(1, 8192)],
                                   render_kw={
                                       "class": "form-control",
                                       "rows": 10})

    tool_command = SelectField('tool_command',
                               choices=get_stats_type_choices(),
                               render_kw={"class": "form-control"},
                               validators=[Optional()])

    tool_parameters = StringField('tool_parameters', validators=[DataRequired(), Length(1, 256)],
                               render_kw={"class": "form-control"})

    submit_button = SubmitField('Submit', render_kw={"class": "btn btn-primary"})