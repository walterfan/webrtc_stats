# Overview

It is a python script to parse the dump file of webrtc-internals


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


