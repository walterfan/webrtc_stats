#!/usr/bin/env python3

import argparse
from copy import deepcopy
from datetime import datetime, timedelta
import json
import os
import sys
import pprint
import matplotlib.pyplot as plt
from matplotlib import dates
from pytz import timezone
import numpy as np
import pandas as pd
from ast import literal_eval

TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

def getWebrtcStatsTypes():
    statsTypes = "inbound-rtp,outbound-rtp,remote-inbound-rtp,transport,candidate-pair,local-candidate,remote-candidate"
    return statsTypes.split(',')

def str2time(str):
    return datetime.strptime(str, TIME_FORMAT).astimezone(timezone('UTC'))

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
        return df

    if all(element == 0 for element in values):
        return df

    time_points = generate_time_series(str2time(row["startTime"]), len(values))
    df =  pd.DataFrame(values)
    df["timestamp"] = time_points
    return df

class WebrtcInternalsAnalyzer:
    """Analyze WebRTC Internals
       Put webrtc stats into pandas DataFrame
    """
    def __init__(self):
        self.time_interval_sec = 1
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
        key = "{}-{}".format(id, name)
        filter1 = self._webrtc_stats[self._webrtc_stats["key"] == key]
        ret = self._webrtc_stats[filter1][["key", "values", "startTime", "endTime"]]
        return ret

    def parse(self, file_name):
        with open(file_name, 'r', encoding='utf_8') as f:
            self._webrtc_internals = {}
            try:
                self._webrtc_internals = json.load(f)
            except:
                print('not a json file {}'.format(file_name))

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
        print("e.g.: ./webrtc_internals_analyze.py -i samples/receiver_webrtc_internals_dump.txt")
        exit(0)

    # judge if json file or not and parse it
    analyzer = WebrtcInternalsAnalyzer()
    analyzer.parse(args.input_file)
    print(analyzer.get_webrtc_stats())

    print("{} webrtc stats ids {}".format('-' * 20, '-' * 20))
    for statsType in getWebrtcStatsTypes():
        print("*", statsType, ":", analyzer.get_stats_ids(statsType))
    #print(json.dumps(pc_stats, indent=2))

    print("{} media stats {}".format('-' * 20, '-' * 20))
    print(analyzer.get_media_stats().keys())

    print("{} inbound-rtp bytesReceived_in_bits/s {}".format('-' * 20, '-' * 20))
    metric_type_name = ("inbound-rtp", "[bytesReceived_in_bits/s]")
    print(metric_type_name)
    print(analyzer.get_stats_by_type_name(metric_type_name[0], metric_type_name[1]))