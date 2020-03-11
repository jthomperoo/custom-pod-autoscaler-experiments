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
import json
import numpy as np
from tabulate import tabulate
from matplotlib import pyplot as plt

def plot_replica_comparison(horizontal_replicas, predictive_replicas):
    plt.figure(figsize=[6, 6])
    plt.plot(list(np.arange(0, 30, 0.5)), horizontal_replicas, "r", list(np.arange(0, 30, 0.5)), predictive_replicas, "b")
    plt.legend(["K8s HPA", "CPA Predictive HPA"])
    plt.xlabel("time (minutes)")
    plt.ylabel("number of replicas")
    plt.savefig("results/predictive_vs_horizontal_replicas.svg")

def plot_avg_latency_comparison(horizontal_latencies, predictive_latencies):
    horizontal_avg_latencies = []
    for result in horizontal_latencies:
        if result["requests"].get("GET_/api/v1/namespaces/default/services/horizontal-deployment/proxy//") is None:
            continue
        horizontal_avg_latencies.append(result["requests"].get("GET_/api/v1/namespaces/default/services/horizontal-deployment/proxy//").get("avg_response_time"))
    predictive_avg_latencies = []
    for result in predictive_latencies:
        if result["requests"].get("GET_/api/v1/namespaces/default/services/predictive-deployment/proxy//") is None:
            continue
        predictive_avg_latencies.append(result["requests"].get("GET_/api/v1/namespaces/default/services/predictive-deployment/proxy//").get("avg_response_time"))
    
    plt.figure(figsize=[6, 6])
    plt.plot(list(np.arange(0, 30, 0.5)), horizontal_avg_latencies, "r", list(np.arange(0, 30, 0.5)), predictive_avg_latencies, "b")
    plt.legend(["K8s HPA", "CPA Predictive HPA"])
    plt.xlabel("time (minutes)")
    plt.ylabel("average latency")
    plt.savefig("results/avg_latency_comparison.svg")


def plot_max_latency_comparison(horizontal_latencies, predictive_latencies):
    horizontal_max_latencies = []
    for result in horizontal_latencies:
        if result["requests"].get("GET_/api/v1/namespaces/default/services/horizontal-deployment/proxy//") is None:
            continue
        horizontal_max_latencies.append(result["requests"].get("GET_/api/v1/namespaces/default/services/horizontal-deployment/proxy//").get("max_response_time"))
    predictive_max_latencies = []
    for result in predictive_latencies:
        if result["requests"].get("GET_/api/v1/namespaces/default/services/predictive-deployment/proxy//") is None:
            continue
        predictive_max_latencies.append(result["requests"].get("GET_/api/v1/namespaces/default/services/predictive-deployment/proxy//").get("max_response_time"))
    
    plt.figure(figsize=[6, 6])
    plt.plot(list(np.arange(0, 30, 0.5)), horizontal_max_latencies, "r", list(np.arange(0, 30, 0.5)), predictive_max_latencies, "b")
    plt.legend(["K8s HPA", "CPA Predictive HPA"])
    plt.xlabel("time (minutes)")
    plt.ylabel("maximum latency")
    plt.savefig("results/max_latency_comparison.svg")

def plot_failed_to_success_request_percentage(horizontal_latencies, predictive_latencies):
    horizontal_fail_percentages = []
    for result in horizontal_latencies:
        if result["requests"].get("GET_/api/v1/namespaces/default/services/horizontal-deployment/proxy//") is None:
            continue
        horizontal_fail_percentages.append(result["num_requests_fail"] / result["num_requests"] * 100)
    predictive_fail_percentages = []
    for result in predictive_latencies:
        if result["requests"].get("GET_/api/v1/namespaces/default/services/predictive-deployment/proxy//") is None:
            continue
        predictive_fail_percentages.append(result["num_requests_fail"] / result["num_requests"] * 100)
    
    plt.figure(figsize=[6, 6])
    plt.plot(list(np.arange(0, 30, 0.5)), horizontal_fail_percentages, "r", list(np.arange(0, 30, 0.5)), predictive_fail_percentages, "b")
    plt.legend(["K8s HPA", "CPA Predictive HPA"])
    plt.xlabel("time (minutes)")
    plt.ylabel("failed requests (%)")
    plt.savefig("results/fail_percentage_comparison.svg")

def create_table(horizontal_replicas, predictive_replicas, horizontal_latencies, predictive_latencies):

    horizontal_num_requests = []
    for result in horizontal_latencies:
        if result["requests"].get("GET_/api/v1/namespaces/default/services/horizontal-deployment/proxy//") is None:
            continue
        horizontal_num_requests.append(result["num_requests"])
    predictive_num_requests = []
    for result in predictive_latencies:
        if result["requests"].get("GET_/api/v1/namespaces/default/services/predictive-deployment/proxy//") is None:
            continue
        predictive_num_requests.append(result["num_requests"])

    horizontal_avg_latencies = []
    for result in horizontal_latencies:
        if result["requests"].get("GET_/api/v1/namespaces/default/services/horizontal-deployment/proxy//") is None:
            continue
        horizontal_avg_latencies.append(result["requests"].get("GET_/api/v1/namespaces/default/services/horizontal-deployment/proxy//").get("avg_response_time"))
    predictive_avg_latencies = []
    for result in predictive_latencies:
        if result["requests"].get("GET_/api/v1/namespaces/default/services/predictive-deployment/proxy//") is None:
            continue
        predictive_avg_latencies.append(result["requests"].get("GET_/api/v1/namespaces/default/services/predictive-deployment/proxy//").get("avg_response_time"))

    horizontal_max_latencies = []
    for result in horizontal_latencies:
        if result["requests"].get("GET_/api/v1/namespaces/default/services/horizontal-deployment/proxy//") is None:
            continue
        horizontal_max_latencies.append(result["requests"].get("GET_/api/v1/namespaces/default/services/horizontal-deployment/proxy//").get("max_response_time"))
    predictive_max_latencies = []
    for result in predictive_latencies:
        if result["requests"].get("GET_/api/v1/namespaces/default/services/predictive-deployment/proxy//") is None:
            continue
        predictive_max_latencies.append(result["requests"].get("GET_/api/v1/namespaces/default/services/predictive-deployment/proxy//").get("max_response_time"))

    horizontal_fail_percentages = []
    for result in horizontal_latencies:
        if result["requests"].get("GET_/api/v1/namespaces/default/services/horizontal-deployment/proxy//") is None:
            continue
        horizontal_fail_percentages.append(result["num_requests_fail"] / result["num_requests"] * 100)
    predictive_fail_percentages = []
    for result in predictive_latencies:
        if result["requests"].get("GET_/api/v1/namespaces/default/services/predictive-deployment/proxy//") is None:
            continue
        predictive_fail_percentages.append(result["num_requests_fail"] / result["num_requests"] * 100)

    table = {
        "time (mins)": list(np.arange(0, 30, 0.5)),
        "hpa num requests": horizontal_num_requests,
        "phpa num requests": predictive_num_requests,
        "hpa replicas": horizontal_replicas,
        "phpa replicas": predictive_replicas,
        "hpa avg latencies": horizontal_avg_latencies,
        "phpa avg latencies": predictive_avg_latencies,
        "hpa max latencies": horizontal_max_latencies,
        "phpa max latencies": predictive_max_latencies,
        "hpa fail requests (%)": horizontal_fail_percentages,
        "phpa fail requests (%)": predictive_fail_percentages
    }

    with open("results/predictive_vs_horizontal_table.md", "w") as table_file:
        table_file.write(tabulate(table, tablefmt="pipe", headers="keys"))

def main():
    with open("results/results.json") as json_file:
        results = json.load(json_file)
    horizontal_replicas = results["horizontal"]["replicas"]
    predictive_replicas = results["predictive"]["replicas"]
    horizontal_latencies = results["horizontal"]["latency"]
    predictive_latencies = results["predictive"]["latency"]
    horizontal_latencies = sorted(horizontal_latencies, key=lambda k: k["start_time"])
    predictive_latencies = sorted(predictive_latencies, key=lambda k: k["start_time"])
    create_table(horizontal_replicas, predictive_replicas, horizontal_latencies, predictive_latencies)
    plot_replica_comparison(horizontal_replicas, predictive_replicas)
    plot_avg_latency_comparison(horizontal_latencies, predictive_latencies)
    plot_max_latency_comparison(horizontal_latencies, predictive_latencies)
    plot_failed_to_success_request_percentage(horizontal_latencies, predictive_latencies)


if __name__ == "__main__":
    main()
