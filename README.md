# Overview

It is a python script to parse the dump file of webrtc-internals

# Progress

30%, will add a simple web app for query metrics and draw related chart

# Metrics

When we open `chrome://webrtc-internals/` in chrome,
or open `edge://webrtc-internals/` in edge,
or open `about:webrtc` in firefox


We can see the following info and metrics

* ICE connection state
* Signaling state
* ICE candidate grid
* ICE connection candidate pair and related metrics
* Inbound RTP and remote inbound RTP stream metrics
* Outbound RTP and remote outbound RTP stream metrics


We need pay more attention to

* Candidate-pair
* Local-candidate
* Remote-candidate
* Inbound-rtp
* Outbound-rtp
* Opus codec: maxaveragebitrate, maxplaybackrate, stereo, useinbandfec, etc.
* H264 codec: level-asymmetry-allowed, max-br, max-dpb, max-fps, max-fs, max-mbps, packetization-mode, profile-level-id, id, etc.



# Front end page

A simple flask based app

```
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt

source ./venv/bin/activate
export FLASK_DEBUG=1
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=8000 &
```