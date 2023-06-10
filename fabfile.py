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
from pytz import timezone
from datetime import datetime, timedelta
import webrtc_internals_analyzer as wia
import pandas as pd

DEFAULT_HOSTS = ["localhost"]
DEFAULT_PATH = os.getcwd()

def get_log_path(file):
    if not file.startswith("/"):
        return "{}/{}".format(DEFAULT_PATH, file)
    else:
        return file

def get_stats_values(media_stats, stats_id, stats_name):
    stats_key = f"{stats_id}-{stats_name}"

    df = media_stats.get(stats_key, [])
    if len(df) == 0:
        return df
    df['timestamp']=df['timestamp'].dt.strftime('%H:%M:%S')

    return df

@task(hosts=DEFAULT_HOSTS)
def candidate_pair_stats(c, file):
    """
    fab candidate-pair-stats -f samples/receiver_webrtc_internals_dump.txt
    """
    log_file = get_log_path(file)
    category="candidate-pair"
    analyzer = wia.WebrtcInternalsAnalyzer()
    analyzer.parse(log_file)
    stats_ids = analyzer.get_stats_ids(category)

    media_stats = analyzer.get_media_stats()
    stats_items = ["availableOutgoingBitrate","availableIncomingBitrate", "[bytesSent_in_bits/s]", "[bytesReceived_in_bits/s]", "currentRoundTripTime"]
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


        print(f"\n# {category}: {stats_id} {local_protocol} from {local_ip}:{local_port} to {remote_ip}:{remote_port}\n")
        for stats_item in stats_items:
            stats_df = get_stats_values(media_stats, stats_id, stats_item)
            if len(stats_df) == 0:
                continue
            print(f"* {stats_id}-{stats_item}: ", stats_df.tail(6)["value"].values.tolist())