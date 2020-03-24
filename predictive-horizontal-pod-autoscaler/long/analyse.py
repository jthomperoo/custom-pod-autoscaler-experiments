# Copyright 2020 Jamie Thompson.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import csv
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)

def plot_replica_comparison(svg_name, hpa_replicas, hpa_latency, phpa_replicas, phpa_latency):
    fig, axs = plt.subplots(2, 2,figsize=[15,15])

    axs[0,0].plot(hpa_replicas["time"], hpa_replicas["replicas"], color="green")
    axs[0,0].legend(["hpa replica count"], loc="upper left")
    axs[0,0].set_xlabel("time")
    axs[0,0].set_ylabel("number of replicas")
    axs[0,0].set_title("replica count for hpa over time")

    axs[1,0].set_ylabel("number of requests")
    axs[1,0].plot(hpa_latency["time"], hpa_latency["num_requests"], color="green")
    axs[1,0].legend(["hpa number of requests"], loc="upper right")
    axs[1,0].set_title("number of requests for hpa over time")

    axs[0,1].plot(phpa_replicas["time"], phpa_replicas["replicas"], color="purple")
    axs[0,1].legend(["phpa replica count"], loc="upper left")
    axs[0,1].set_xlabel("time")
    axs[0,1].set_ylabel("number of replicas")
    axs[0,1].set_title("replica count for phpa over time")

    axs[1,1].set_ylabel("number of requests")
    axs[1,1].plot(phpa_latency["time"], phpa_latency["num_requests"], color="purple")
    axs[1,1].legend(["phpa number of requests"], loc="upper right")
    axs[1,1].set_title("number of requests for phpa over time")

    for i in range(2):
        for j in range(2):
            xax = axs[i,j].get_xaxis()
            xax.set_major_locator(mdates.DayLocator())
            xax.set_major_formatter(mdates.DateFormatter("Day %d"))
            xax.set_minor_locator(mdates.HourLocator(byhour=range(0, 24, 4)))
            xax.set_minor_formatter(mdates.DateFormatter("%H"))
            xax.set_tick_params(which="major", pad=15)

    fig.tight_layout()
    plt.savefig(f"results/{svg_name}.svg")


def plot_latency_comparison(svg_name, latency):
    fig, ax1 = plt.subplots(figsize=[10,10])

    ax1.plot(latency["time"], latency["avg_response_time"])
    ax1.plot(latency["time"], latency["min_response_time"])
    ax1.plot(latency["time"], latency["max_response_time"])
    ax1.legend(["average latency", "minimum latency", "maximum latency"], loc="upper left")
    ax1.set_xlabel("time")
    ax1.set_ylabel("latency")
    ax1.xaxis.set_tick_params(which="major", pad=15)

    ax2 = ax1.twinx()

    ax2.set_ylabel("number of requests")
    ax2.plot(latency["time"], latency["num_requests"], color="purple")
    ax2.legend(["number of requests"], loc="upper right")

    xax = ax2.get_xaxis()
    xax.set_major_locator(mdates.DayLocator())
    xax.set_major_formatter(mdates.DateFormatter("Day %d"))
    xax.set_minor_locator(mdates.HourLocator(byhour=range(0, 24, 2)))
    xax.set_minor_formatter(mdates.DateFormatter("%H"))

    fig.tight_layout()
    plt.savefig(f"results/{svg_name}.svg")

def plot_avg_latency_comparison(svg_name, hpa_latency, phpa_latency):
    fig, axs = plt.subplots(2, 2,figsize=[15,15])
    axs[0,0].plot(hpa_latency["time"], hpa_latency["avg_response_time"], color="green")
    axs[0,0].legend(["hpa average latency"], loc="upper left")
    axs[0,0].set_xlabel("time")
    axs[0,0].set_ylabel("number of replicas")
    axs[0,0].set_title("average latency for hpa over time")
    axs[0,0].set_ylim([0,600])

    axs[1,0].set_ylabel("number of requests")
    axs[1,0].plot(hpa_latency["time"], hpa_latency["num_requests"], color="green")
    axs[1,0].legend(["hpa number of requests"], loc="upper right")
    axs[1,0].set_title("number of requests for hpa over time")

    axs[0,1].plot(phpa_latency["time"], phpa_latency["avg_response_time"], color="purple")
    axs[0,1].legend(["phpa average latency"], loc="upper left")
    axs[0,1].set_xlabel("time")
    axs[0,1].set_ylabel("number of replicas")
    axs[0,1].set_title("average latency for phpa over time")
    axs[0,1].set_ylim([0,600])

    axs[1,1].set_ylabel("number of requests")
    axs[1,1].plot(phpa_latency["time"], phpa_latency["num_requests"], color="purple")
    axs[1,1].legend(["phpa number of requests"], loc="upper right")
    axs[1,1].set_title("number of requests for phpa over time")

    for i in range(2):
        for j in range(2):
            xax = axs[i,j].get_xaxis()
            xax.set_major_locator(mdates.DayLocator())
            xax.set_major_formatter(mdates.DateFormatter("Day %d"))
            xax.set_minor_locator(mdates.HourLocator(byhour=range(0, 24, 4)))
            xax.set_minor_formatter(mdates.DateFormatter("%H"))
            xax.set_tick_params(which="major", pad=15)

    fig.tight_layout()
    plt.savefig(f"results/{svg_name}.svg")

def plot_avg_latency_comparison_day(svg_name, day, hpa_latency, phpa_latency):
    fig, axs = plt.subplots(2, 2,figsize=[15,15])
    axs[0,0].plot(hpa_latency["time"], hpa_latency["avg_response_time"], color="green")
    axs[0,0].legend(["hpa average latency"], loc="upper left")
    axs[0,0].set_xlabel("time")
    axs[0,0].set_ylabel("number of replicas")
    axs[0,0].set_title("average latency for hpa over time")
    axs[0,0].set_ylim([0,600])
    axs[0,0].set_xlim([hpa_latency["time"].min() + pd.to_timedelta((day-1)*24*60*60, unit='s'),hpa_latency["time"].min() + pd.to_timedelta(day*24*60*60, unit='s')])

    axs[1,0].set_ylabel("number of requests")
    axs[1,0].plot(hpa_latency["time"], hpa_latency["num_requests"], color="green")
    axs[1,0].legend(["hpa number of requests"], loc="upper right")
    axs[1,0].set_title("number of requests for hpa over time")
    axs[1,0].set_xlim([hpa_latency["time"].min() + pd.to_timedelta((day-1)*24*60*60, unit='s'),hpa_latency["time"].min() + pd.to_timedelta(day*24*60*60, unit='s')])

    axs[0,1].plot(phpa_latency["time"], phpa_latency["avg_response_time"], color="purple")
    axs[0,1].legend(["phpa average latency"], loc="upper left")
    axs[0,1].set_xlabel("time")
    axs[0,1].set_ylabel("number of replicas")
    axs[0,1].set_title("average latency for phpa over time")
    axs[0,1].set_ylim([0,600])
    axs[0,1].set_xlim([phpa_latency["time"].min() + pd.to_timedelta((day-1)*24*60*60, unit='s'),phpa_latency["time"].min() + pd.to_timedelta(day*24*60*60, unit='s')])

    axs[1,1].set_ylabel("number of requests")
    axs[1,1].plot(phpa_latency["time"], phpa_latency["num_requests"], color="purple")
    axs[1,1].legend(["phpa number of requests"], loc="upper right")
    axs[1,1].set_title("number of requests for phpa over time")
    axs[1,1].set_xlim([phpa_latency["time"].min() + pd.to_timedelta((day-1)*24*60*60, unit='s'),phpa_latency["time"].min() + pd.to_timedelta(day*24*60*60, unit='s')])

    for i in range(2):
        for j in range(2):
            xax = axs[i,j].get_xaxis()
            xax.set_major_locator(mdates.DayLocator())
            xax.set_major_formatter(mdates.DateFormatter("Day %d"))
            xax.set_minor_locator(mdates.HourLocator(byhour=range(0, 24, 4)))
            xax.set_minor_formatter(mdates.DateFormatter("%H"))
            xax.set_tick_params(which="major", pad=15)

    fig.tight_layout()
    plt.savefig(f"results/{svg_name}.svg")

def plot_max_latency_comparison_day(svg_name, day, hpa_latency, phpa_latency):
    fig, axs = plt.subplots(2, 2,figsize=[15,15])
    axs[0,0].plot(hpa_latency["time"], hpa_latency["max_response_time"], color="green")
    axs[0,0].legend(["hpa maximum latency"], loc="upper left")
    axs[0,0].set_xlabel("time")
    axs[0,0].set_ylabel("number of replicas")
    axs[0,0].set_title("maximum latency for hpa over time")
    axs[0,0].set_ylim([0,6000])
    axs[0,0].set_xlim([hpa_latency["time"].min() + pd.to_timedelta((day-1)*24*60*60, unit='s'),hpa_latency["time"].min() + pd.to_timedelta(day*24*60*60, unit='s')])

    axs[1,0].set_ylabel("number of requests")
    axs[1,0].plot(hpa_latency["time"], hpa_latency["num_requests"], color="green")
    axs[1,0].legend(["hpa number of requests"], loc="upper right")
    axs[1,0].set_title("number of requests for hpa over time")
    axs[1,0].set_xlim([hpa_latency["time"].min() + pd.to_timedelta((day-1)*24*60*60, unit='s'),hpa_latency["time"].min() + pd.to_timedelta(day*24*60*60, unit='s')])

    axs[0,1].plot(phpa_latency["time"], phpa_latency["max_response_time"], color="purple")
    axs[0,1].legend(["phpa maximum latency"], loc="upper left")
    axs[0,1].set_xlabel("time")
    axs[0,1].set_ylabel("number of replicas")
    axs[0,1].set_title("maximum latency for phpa over time")
    axs[0,1].set_ylim([0,6000])
    axs[0,1].set_xlim([phpa_latency["time"].min() + pd.to_timedelta((day-1)*24*60*60, unit='s'),phpa_latency["time"].min() + pd.to_timedelta(day*24*60*60, unit='s')])

    axs[1,1].set_ylabel("number of requests")
    axs[1,1].plot(phpa_latency["time"], phpa_latency["num_requests"], color="purple")
    axs[1,1].legend(["phpa number of requests"], loc="upper right")
    axs[1,1].set_title("number of requests for phpa over time")
    axs[1,1].set_xlim([phpa_latency["time"].min() + pd.to_timedelta((day-1)*24*60*60, unit='s'),phpa_latency["time"].min() + pd.to_timedelta(day*24*60*60, unit='s')])

    for i in range(2):
        for j in range(2):
            xax = axs[i,j].get_xaxis()
            xax.set_major_locator(mdates.DayLocator())
            xax.set_major_formatter(mdates.DateFormatter("Day %d"))
            xax.set_minor_locator(mdates.HourLocator(byhour=range(0, 24, 4)))
            xax.set_minor_formatter(mdates.DateFormatter("%H"))
            xax.set_tick_params(which="major", pad=15)

    fig.tight_layout()
    plt.savefig(f"results/{svg_name}.svg")

def plot_max_latency_comparison(svg_name, hpa_latency, phpa_latency):
    fig, axs = plt.subplots(2, 2,figsize=[15,15])
    axs[0,0].plot(hpa_latency["time"], hpa_latency["max_response_time"], color="green")
    axs[0,0].legend(["hpa maximum latency"], loc="upper left")
    axs[0,0].set_xlabel("time")
    axs[0,0].set_ylabel("number of replicas")
    axs[0,0].set_title("maximum latency for hpa over time")

    axs[1,0].set_ylabel("number of requests")
    axs[1,0].plot(hpa_latency["time"], hpa_latency["num_requests"], color="green")
    axs[1,0].legend(["hpa number of requests"], loc="upper right")
    axs[1,0].set_title("number of requests for hpa over time")

    axs[0,1].plot(phpa_latency["time"], phpa_latency["max_response_time"], color="purple")
    axs[0,1].legend(["phpa maximum latency"], loc="upper left")
    axs[0,1].set_xlabel("time")
    axs[0,1].set_ylabel("number of replicas")
    axs[0,1].set_title("maximum latency for phpa over time")

    axs[1,1].set_ylabel("number of requests")
    axs[1,1].plot(phpa_latency["time"], phpa_latency["num_requests"], color="purple")
    axs[1,1].legend(["phpa number of requests"], loc="upper right")
    axs[1,1].set_title("number of requests for phpa over time")

    for i in range(2):
        for j in range(2):
            xax = axs[i,j].get_xaxis()
            xax.set_major_locator(mdates.DayLocator())
            xax.set_major_formatter(mdates.DateFormatter("Day %d"))
            xax.set_minor_locator(mdates.HourLocator(byhour=range(0, 24, 4)))
            xax.set_minor_formatter(mdates.DateFormatter("%H"))
            xax.set_tick_params(which="major", pad=15)

    fig.tight_layout()
    plt.savefig(f"results/{svg_name}.svg")

def main():
    hpa_replicas = pd.read_csv("results/hpa/replicas.csv", header=None, names=["time", "replicas"])
    hpa_latency = pd.read_csv("results/hpa/load.csv", header=None, 
        names=["time", "num_requests", "num_requests_fail","avg_response_time","min_response_time","max_response_time"])
    hpa_start = hpa_replicas["time"][0]
    hpa_latency["time"] = [x - hpa_start for x in hpa_latency["time"]]
    hpa_replicas["time"] = [x - hpa_start for x in hpa_replicas["time"]]
    hpa_replicas["time"] = pd.to_datetime(hpa_replicas["time"], unit="s")
    hpa_latency["time"] = pd.to_datetime(hpa_latency["time"], unit="s")
    hpa_replicas = hpa_replicas[1:]
    hpa_latency = hpa_latency[1:]

    phpa_replicas = pd.read_csv("results/phpa/replicas.csv", header=None, names=["time", "replicas"])
    phpa_latency = pd.read_csv("results/phpa/load.csv", header=None, 
        names=["time", "num_requests", "num_requests_fail","avg_response_time","min_response_time","max_response_time"])
    phpa_start = phpa_replicas["time"][0]
    phpa_latency["time"] = [x - phpa_start for x in phpa_latency["time"]]
    phpa_replicas["time"] = [x - phpa_start for x in phpa_replicas["time"]]
    phpa_replicas["time"] = pd.to_datetime(phpa_replicas["time"], unit="s")
    phpa_latency["time"] = pd.to_datetime(phpa_latency["time"], unit="s")
    phpa_replicas = phpa_replicas[1:]
    phpa_latency = phpa_latency[1:]
    
    plot_replica_comparison("replica_compare", hpa_replicas, hpa_latency, phpa_replicas, phpa_latency)
    plot_latency_comparison("hpa_latency", hpa_latency)
    plot_latency_comparison("phpa_latency", phpa_latency)
    plot_avg_latency_comparison("avg_latency_compare", hpa_latency, phpa_latency)
    plot_avg_latency_comparison_day("avg_latency_day_1", 1, hpa_latency, phpa_latency)
    plot_avg_latency_comparison_day("avg_latency_day_2", 2, hpa_latency, phpa_latency)
    plot_avg_latency_comparison_day("avg_latency_day_3", 3, hpa_latency, phpa_latency)
    plot_max_latency_comparison("max_latency_compare", hpa_latency, phpa_latency)
    plot_max_latency_comparison_day("max_latency_day_1", 1, hpa_latency, phpa_latency)
    plot_max_latency_comparison_day("max_latency_day_2", 2, hpa_latency, phpa_latency)
    plot_max_latency_comparison_day("max_latency_day_3", 3, hpa_latency, phpa_latency)

if __name__ == "__main__":
    main()
