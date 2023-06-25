import os
import sys
import matplotlib.pyplot as plt
from fabric import task
from fabric import Connection
import time
import json
import pprint
import os
import platform
import socket
from tabulate import tabulate
from pytz import timezone
from datetime import datetime, timedelta
import pandas as pd
import src.webrtc_stats.analyzer as ws_analyzer
import src.webrtc_stats.analyzer_util as ws_util
from src.webrtc_stats.yaml_config import YamlConfig


DEFAULT_HOSTS = ["localhost"]
DEFAULT_PATH = os.getcwd()

def get_log_path(file):
    if not file.startswith("/"):
        return "{}/{}".format(DEFAULT_PATH, file)
    else:
        return file


@task(hosts=DEFAULT_HOSTS)
def local_ip(c):
    print(ws_util.get_host_ip())


@task(hosts=DEFAULT_HOSTS)
def frontend(c):
    cmds = [
        "cd frontend",
        "export FLASK_APP=app",
        "export FLASK_ENV=development",
        "flask run"
    ]

    for cmd in cmds:
        c.local(cmd)


@task(hosts=DEFAULT_HOSTS)
def media_stats(c, file, name, type="", id="", output=None):
    """
    usage:
    - fab media-stats -f samples/receiver_webrtc_internals_dump.txt -t inbound-rtp -n [bytesReceived_in_bits/s]
    - fab media-stats -f $TA_LOG_DIR/10.224.34.19_webrtc_internals_dump.txt -n "[framesDecoded/s]"  -i IT01V3609914274
    """
    log_file = get_log_path(file)
    analyzer = ws_analyzer.WebrtcInternalsAnalyzer()
    analyzer.parse(log_file)
    if type:
        stats_df = analyzer.get_stats_by_type_name(type, name)
        print(stats_df)
    if id:
        #stats_df = analyzer.get_stats_by_id_name(id, name)
        stats_df = analyzer.get_stats_values(id, name)
        print(tabulate(stats_df, headers='keys', tablefmt='psql'))
        if output and output.endswith(".csv"):
            stats_df.to_csv(output)



@task(hosts=DEFAULT_HOSTS)
def rtp_stats(c, file, category, bitrate_item):
    """
    usage: fab rtp-stats -f samples/sender_webrtc_internals_dump.txt -c outbound-rtp -b "[bytesSent_in_bits/s]"
    """

    log_file = get_log_path(file)
    analyzer = ws_analyzer.WebrtcInternalsAnalyzer()
    analyzer.parse(log_file)
    stats_ids = analyzer.get_stats_ids(category)

    yamlConfig = YamlConfig("src/webrtc_stats/analyzer.yaml")
    stats_items = yamlConfig.get_config().get("media_stats").get(category)

    for stats_id in stats_ids:

        bitrate_df = analyzer.get_stats_values(stats_id, bitrate_item)
        if len(bitrate_df) == 0:
            continue

        print(f"\n# {category}: {stats_id}\n")

        for stats_item in stats_items:
            stats_df = analyzer.get_stats_values(stats_id, stats_item)
            if len(stats_df) == 0:
                continue
            print(f"* {stats_id}-{stats_item}: ", stats_df.tail(10)["value"].values.tolist())


@task(hosts=DEFAULT_HOSTS)
def outbound_rtp_stats(c, file):
    """
    usage: fab outbound-rtp-stats -f samples/sender_webrtc_internals_dump.txt
    """
    category="outbound-rtp"
    bitrate_item = "[bytesSent_in_bits/s]"

    rtp_stats(c, file, category, bitrate_item)

@task(hosts=DEFAULT_HOSTS)
def inbound_rtp_stats(c, file):
    """
    usage: fab inbound-rtp-stats -f samples/receiver_webrtc_internals_dump.txt
    """
    category="inbound-rtp"
    bitrate_item = "[bytesReceived_in_bits/s]"

    rtp_stats(c, file, category, bitrate_item)

@task(hosts=DEFAULT_HOSTS)
def candidate_pair_stats(c, file):
    """
    usage: fab candidate-pair-stats -f samples/receiver_webrtc_internals_dump.txt
    """
    category="candidate-pair"
    stats_items = ["availableOutgoingBitrate",
                   "availableIncomingBitrate",
                   "[bytesSent_in_bits/s]",
                   "[bytesReceived_in_bits/s]",
                   "currentRoundTripTime"]

    log_file = get_log_path(file)
    analyzer = ws_analyzer.WebrtcInternalsAnalyzer()
    analyzer.parse(log_file)
    stats_ids = analyzer.get_stats_ids(category)
    i = 0
    media_stats = analyzer.get_media_stats()
    for stats_id in stats_ids:
        stats_key = f"{stats_id}-nominated"

        df = media_stats.get(stats_key, [])
        if len(df) == 0:
            continue

        local_candidate_id = analyzer.get_unique_value(stats_id, "localCandidateId")
        remote_candidate_id = analyzer.get_unique_value(stats_id, "remoteCandidateId")

        local_protocol = analyzer.get_unique_value(local_candidate_id, "protocol")
        local_ip = analyzer.get_unique_value(local_candidate_id, "ip")
        local_port = analyzer.get_unique_value(local_candidate_id, "port")

        remote_protocol = analyzer.get_unique_value(remote_candidate_id, "protocol")
        remote_ip = analyzer.get_unique_value(remote_candidate_id, "ip")
        remote_port = analyzer.get_unique_value(remote_candidate_id, "port")

        i = i + 1
        print(f"\n# {i}. {category}: {stats_id} {local_protocol} from {local_ip}:{local_port} to {remote_ip}:{remote_port}\n")
        for stats_item in stats_items:
            stats_df = analyzer.get_stats_values(stats_id, stats_item)
            if len(stats_df) == 0:
                continue
            print(f"* {stats_id}-{stats_item}: ", stats_df.tail(6)["value"].values.tolist())

