#!/usr/bin/env python3

import argparse
from copy import deepcopy
from datetime import datetime, timedelta
import os
import json
import matplotlib.pyplot as plt
from matplotlib import dates
from pytz import timezone
import numpy as np
import pandas as pd
from ast import literal_eval
from tabulate import tabulate
from . import analyze_util

logger = analyze_util.get_logger(os.path.basename(__file__))

def getWebrtcStatsTypes():
    statsTypes = "inbound-rtp,outbound-rtp,remote-inbound-rtp,transport,candidate-pair,local-candidate,remote-candidate"
    return statsTypes.split(',')

def generate_time_series(start_time, num_points, interval=timedelta(seconds=1)):
    timestamps = []
    current_time = start_time

    for _ in range(num_points):
        timestamps.append(current_time)
        current_time += interval

    return timestamps

def create_df_from_values(row):
    df = pd.DataFrame()
    metrics_str = row['values']
    if "false" in metrics_str:
        metrics_str = metrics_str.replace("false", "False")
    if "true" in metrics_str:
        metrics_str = metrics_str.replace("true", "True")

    try:
        values = literal_eval(metrics_str)
    except:
        print("unrecognize {}".format(metrics_str))
        return df

    if type(values) != list:
        print("not list")
        return df

    if all(element == 0 for element in values):
        #print("all is zero")
        return df

    time_points = generate_time_series(analyze_util.str2time(row["startTime"]), len(values))
    df =  pd.DataFrame()
    df["timestamp"] = time_points
    df["value"] = values
    return df

class WebrtcInternalsAnalyzer:
    """Analyze WebRTC Internals
       Put webrtc stats into pandas DataFrame
    """
    def __init__(self):

        self._webrtc_internals = {}

        # a data frame: key (id-name), values, statsType, startTime, endTime
        self._webrtc_stats = pd.DataFrame()
        self._webrtc_events = pd.DataFrame()

        # dict of array for media stats
        self._pc_stats = []
        # dict of array for media events
        self._pc_events = []

        # key is metrics id-name, values is a dataframe: "timestamp, value"
        self._media_stats = {}

    def get_webrtc_stats(self):
        return self._webrtc_stats

    def get_media_stats(self):
        return self._media_stats

    def get_webrtc_events(self):
        return self.get_webrtc_events

    def get_stats_ids(self, statsType):
        media_stats = self._webrtc_stats[self._webrtc_stats["statsType"] == statsType]
        metrics_ids = pd.unique(media_stats["id"])
        return metrics_ids

    def get_metrics_values(self, statsDf):
        media_stats = {}
        for index, row in statsDf.iterrows():
            df = create_df_from_values(row)
            if len(df) > 0:
                media_stats[row['key']] = df
        return media_stats

    def get_stats_by_type_name(self, statsType, statsName):
        filter1 = self._webrtc_stats["statsType"] == statsType
        filter2 = self._webrtc_stats["name"] == statsName
        ret = self._webrtc_stats[filter1 & filter2][["key", "values", "startTime", "endTime"]]
        return ret

    def get_stats_by_id_name(self, id, name):
        filter1 = self._webrtc_stats["name"] == name
        filter2 = self._webrtc_stats["id"] == id
        ret = self._webrtc_stats[filter1 & filter2][["key", "values", "startTime", "endTime"]]
        return ret

    def get_stats_by_type_id(self, statsType, statsId):
        filter1 = self._webrtc_stats["statsType"] == statsType
        filter2 = self._webrtc_stats["id"] == statsId
        ret = self._webrtc_stats[filter1 & filter2][["key", "values", "startTime", "endTime"]]
        return ret


    def get_unique_value(self, stats_id, stats_name):

        stats_df = self.get_stats_by_id_name(stats_id, stats_name)
        values_df = create_df_from_values(stats_df.squeeze())
        stats_values = pd.unique(values_df["value"])
        if len(stats_values) == 1:
            stats_value = stats_values[0]
            return stats_value

        return None

    def parse(self, file_name):
        with open(file_name, 'r', encoding='utf_8') as f:
            logger.info(f"open {file_name}")
            self._webrtc_internals = {}
            try:
                self._webrtc_internals = json.load(f)
            except:
                logger.errror('not a json file {}'.format(file_name))

            for pcKey, pcValue in self._webrtc_internals['PeerConnections'].items():
                pcStats = pcValue["stats"]

                for itemKey, itemDict in pcValue.items():

                    if itemKey == "stats":

                        for statKey, statDict in itemDict.items():
                            statsItem = {}
                            statsItem["key"] = statKey
                            statsItem["pc"] = pcKey
                            if "-" in statKey:
                                arr = statKey.split("-")
                                statsItem["id"] = arr[0]
                                statsItem["name"] = arr[1]

                            statsItem.update(statDict)
                            self._pc_stats.append(statsItem)

                    elif itemKey == "updateLog":
                        self._pc_events = itemDict
                    else:
                        pass

        self._webrtc_stats = pd.DataFrame.from_records(self._pc_stats)

        self._webrtc_events = pd.DataFrame.from_records(self._pc_events)

        self._media_stats = self.get_metrics_values(self._webrtc_stats)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', action='store',
                        dest='input_file', help='input webrtc dump file')

    parser.add_argument('-c', action='store', dest='config_file',
                        help='user specified config file, yaml format only, will replace default config file')

    args = parser.parse_args()

    if not args.input_file:
        print('error: required input file')
        print("e.g.: ./webrtc_internals_analyzer.py -i samples/receiver_webrtc_internals_dump.txt")
        exit(0)

    # judge if json file or not and parse it
    analyzer = WebrtcInternalsAnalyzer()
    analyzer.parse(args.input_file)
    line_separator = '-' * 30
    print(f"\n{line_separator} webrtc media stats {line_separator}")
    print(analyzer.get_webrtc_stats())

    print(f"\n{line_separator} webrtc stats ids {line_separator}")
    for statsType in getWebrtcStatsTypes():
        stats_ids = analyzer.get_stats_ids(statsType)
        print("*", statsType, ":", stats_ids.tolist())

    metric_type_names = [
        ("inbound-rtp", "[bytesReceived_in_bits/s]"),
        ("outbound-rtp", "[bytesSent_in_bits/s]")
    ]
    for metric_type_name in metric_type_names:
        print(f"\n{line_separator} {metric_type_name} {line_separator}")
        print(analyzer.get_stats_by_type_name(metric_type_name[0], metric_type_name[1]))