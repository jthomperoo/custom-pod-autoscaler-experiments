---
title: Kubernetes Custom Autoscaling
author: Jamie Thompson
date: 24/04/2020
---

# Introduction

Kubernetes in its current state allows setting how many pods a deployment has, 
allowing you to set a target amount of pods it should have and Kubernetes will 
reconcile this and ensure that it reaches that target.  

Kubernetes provides the Horizontal Pod Autoscaler (HPA) which allows automatic 
scaling of the number of pods a deployment has based on metrics that you feed 
into the HPA. Generally these metrics are CPU/memory load of the pod, allowing 
scaling up if the load gets too much or down if resources are underutilized; 
but also includes custom metrics defined through the metrics API. The HPA takes 
these metrics and applies a built in algorithm to them to determine the number 
of pods to scale up/down.

## Problems

There are two problems in the current Kubernetes HPA setup:

- Hard-coded algorithm with less flexibility.
- Custom metrics can be difficult to set up.

### Hard-coded Algorithm

The built in algorithm may not suit your needs; you may require more complex 
scaling logic. The only way to currently resolve this is to write your own 
scaler from scratch, which is a complex and difficult task - with an added 
vector of failure if there are bugs in your scaling. Writing this scaler 
requires an intimate understanding of Kubernetes and its APIs.

### Custom Metrics Difficulty

Custom metrics requires the use of third party adapters (e.g. Prometheus), or 
requires the user to write their own adapter. This requires a lot of 
configuration, and in the case of writing their own adapter requires in-depth 
Kubernetes API knowledge.

## Existing Attempts at Solutions

### Horizontal Pod Autoscaler with Custom Metrics

### Agones Fleet Autoscaler

# Solution

The Custom Pod Autoscaler Framework (CPAF) is designed to address these two 
problems. The CPAF would work by allowing the creation of Custom Pod 
Autoscalers (CPA) and letting them run inside a Kubernetes cluster.  

The CPA would contain custom user defined logic for scaling, alongside a base 
program to handle interactions with Kubernetes and triggering the user defined 
logic. The CPA would allow for very simple scaling code to be written, in a 
variety of languages and with different technologies, while hiding the 
complexities of Kubernetes.

## Customisation

A CPA would contain a base program that would interact with user provided 
logic; which can be in the form of any executable code such as Python script, 
or it could even be a separate service which would respond to HTTP requests. 
The CPA would define a standard API for interacting with the CPA; using this 
users could write their own logic to interact with it.  

Primarily a series of inputs and ouputs would be defined, to allow user logic 
to be created that can reliably execute based on input and produce parsable 
results. This would allow for essentially any program or logic to be used as 
part of an autoscaler; using any language or framework, as long as it can run 
inside a Docker container.  

Alongside this the CPA base program itself should be highly customisable; 
allowing customising on the same lines that the Horizontal Pod Autoscaler can 
be customised; for example setting the interval between making autoscaling 
decisions. The CPA base program should allow customisation at both deploy time 
and build time, to allow autoscaler developers to set sensible default values, 
whilst also allowing users of the autoscaler to customise it to their needs.

## Ease of Use

Both creating a CPA and deploying it should be easy, and not require lots of 
configuration, third party deployments or intricate Kubernetes API knowledge.

### Creating a Custom Pod Autoscaler

CPAs should be extremely flexible in how they are created, supporting a wide 
variety of languages, frameworks, environments, and interfaces.

### Deploying a Custom Pod Autoscaler

CPAs should be deployed in the standard way to deploy to Kubernetes, through 
Kubernetes deployment YAML. This is flexible, and also has the benefit of 
including compatiblity with some other commonly used tools, such as Helm.  

Deploying through Kubernetes YAML provides the benefit of familiarity and 
consistency with other parts of Kubernetes; whilst also allowing more 
transparancy in versioning, resources used, and deploy time customisation.  

The deployment YAML should be as simple as possible, and without obscure or 
confusing resources included; much of the complexity should be abstracted away 
from the deploying user, whilst also retaining a level of customisation at 
deploy time. This could be achieved with a custom Kubernetes resource and some 
logic in the form of a Kubernetes controller or operator for managing the 
resource.  

Once a Custom Pod Autoscaler is deployed, it should be easy to interact with - 
it should provide a versioned HTTP REST API for retrieving information and for 
triggering autoscaling.



# Requirements

## Must Have

- Can deploy a Docker image with autoscaling application into a Kubernetes 
cluster.
- Autoscaler repeatedly runs.
- Supports user logic, can triggered through a shell command, allows 
specification in any language/framework that supports being called through 
shell commands.
    - Supports HTTP requests from user logic.
- If user logic specifies that the number of replicas should change, scaling 
should occur and the number of pods should be adjusted.
- \>= 70% Unit test coverage.
- Can be deployed with Kubernetes YAML.
- Kubernetes Custom Resource specifiying the Custom Pod Autoscaler to allow for 
simpler and easier deployment/configuration.
- Syntax validation for Custom Pod Autoscaler Kubernetes YAML.
- Deploying the Kubernetes Custom Resource should provision all required 
Kubernetes resources for the autoscaler.
- Can deliver configuration options through Kubernetes YAML.
- Can deliver configuration options through a supplied configuration file baked 
into the autoscaler image.
- Configuration options.
    - How frequently the autoscaler runs.
    - Minimum and Maximum replicas
    - Which resource to target for scaling.
    - Timeouts for metric and evaluation gathering.
- Can delete the autoscaler.
    - Deletes all associated Kubernetes resources.

## Should Have

- *Cooldown* feature to avoid *thrashing*.
- Allow choosing which pods to terminate when scaling down.
- Manual triggering of the Custom Pod Autoscaler metric gathering and 
evaluation through an API.
  - Provide a *dry run* flag to the API to allow seeing how the autoscaler 
would scale without applying the results.
- Hooks for different actions/stages in the autoscaling process.
- Support scaling all resources the Horizontal Pod Autoscaler can scale.
  - ReplicaSets.
  - ReplicationControllers.
  - StatefulSets.
  - Deployments.
- Methods for calling user logic.
  - Can trigger user logic through an HTTP request, allowing logic to exist 
outside of the autoscaling pod, or even outside of the cluster.
- Metric gathering modes.
  - Can run in a *per pod* autoscaling mode, which will run metric gathering 
for each pod the targeted resource manages.
  - Can run in a *per resource* autoscaling mode, which will run metric 
gathering only once for the targeted resource.
- Full customisation of Kubernetes resources, allowing Custom Pod Autoscalers 
to define their own resource dependencies.
  - When this customised resource is provided, the Custom Pod Autoscaler should 
have ownership; meaning if the autoscaler is deleted the resource is deleted.
- Custom Pod Autoscaler GUI.
  - GUI to view and manage custom pod autoscalers.
- Implemented Custom Pod Autoscalers
  - Horizontal Pod Autoscaler; reimplemented as a Custom Pod Autoscaler.
  - Predictive Horizontal Pod Autoscaler; Horizontal Pod Autoscaler extended 
with statistical prediction techniques.
  - Load Testing Pod Autoscaler; autoscaler allowing scaling based on realtime 
load tested data.
  - Examples to help developers.
    - Autoscaler written in Python.
    - Autoscaler written in Golang.
    - Autoscaler that scales based on Twitter activity.



# Design

## Custom Pod Autoscaler

A Custom Pod Autoscaler (CPA) would be a single docker image that manages a
deployment, handling scaling. It would be responsible for gathering metrics,
making evaluations and interacting with Kubernetes to scale the deployments it
manages.

### Custom Pod Autoscaler Base

The Custom Pod Autoscaler Base (CPAB) would be a program that would handle all 
complexities when interacting with Kubernetes and the API. This program would 
provide a base for users to write their own logic on top of, while abstracting 
away much of the complexity. The program would be highly configurable.  

The CPAB would be built by me as part of this project. The CPAB would be 
distributed as both a binary and built into a set of Docker images.

#### Autoscaler

The Autoscaler part of the CPAB program would handle the actual scaling
mechanism. This part would be responsible for interacting with the Kubernetes
API and retriving relevant information about the resource being managed, before
feeding this into the user defined logic to gather metrics and retrieve
evaluations. The autoscaler would then take these decisions from the user
defined logic and use them to interact with the Kubernetes API to scale the
resources being managed.  

The Autoscaler would run repeatedly at a set interval, gathering metrics,
evaluating and then scaling. This repeated run would have to run concurrently to
the rest of the application, without blocking any other part of the program.  

The Autoscaler should fail safely; if user defined logic fails or crashes, or 
if the autoscaler itself fails or crashs, it should not affect the resource 
being managed.If the autoscaler crashes or fails, scaling should not occur; 
scaling should only occur if the autoscaler processes all user defined logic 
and calculates an evaluation correctly and without errors.  

#### HTTP API

The CPAB would expose a HTTP REST API for runtime interactions with the CPA. 
The API would allow triggering the autoscaler through a HTTP request, 
retrieving metrics without evaluating, and retrieving evaluations without 
scaling as part of a dry run.  

This API would allow the CPA to be integrated as part of a wider system and 
allow for manual control over the autoscaler.  

The REST API should be versioned and ensure compatiblity across new versions, 
starting at API version `v1`. This would be usable as `/api/<VERSION>/endpoint` 
to prevent 
breaking API changes from disrupting systems/workflows.

#### Configuration Options

### User Defined Logic

User Defined Logic (UDL) would be the customised programs written by users of 
the CPA. The UDL would be split into two parts, metric gathering and 
evaluations. 

#### Methods

UDL would be accessed and triggered through a shell command that would be part
of the configuration options of the CPAB. This would allow for flexibility on
how the user wants to implement their metric gathering and evaluation logic;
they could do it mostly in any way they wanted (Python, Golang, Java etc.). The
only requirement would be that then logic has to be started by a shell command.
Specifications on how UDL should receive data and output results would have to
be created for users to be able to implement their own logic.

#### Metric Gathering

Metric gathering would take in the pods in a deployment being managed, and 
output any metrics it gathers/generates.  

The metric gathering user defined logic should take as input information about 
the resouce being managed, such as a full deployment description and 
specification in JSON, or a full pod description and specification. The input 
into the metric gatherer should also describe the circumstances that the user 
defined logic is being run with; for example if it was caused by an API being 
triggered, if it is a dry run of the API or if it was a scheduled autoscale. 
This should be provided in a parsable and standard way, for example as JSON.  

The metric gathering user defined logic

#### Evaluating

The evaluation would take the metrics gathered/generated by the metric 
gathering and make a decision on how to scale a deployment, outputting its 
decision.

### Kubernetes Resources

Running the CPA in a Kubernetes cluster would require some configuration in the
cluster. The CPA would require a single pod deployment to run in; Kubernetes
would manage this deployment. Further configuration is also required to allow
the CPA to interact with deployments and pods in the cluster; requiring a
Service Account, a Role and a Role Binding. This could be manually set up by the
user, but could be difficult to set up and time consuming, to address this an
operator would be offered to allow easy install.  

Required Resources:  

- Deployment.
- Service Account.
- Role.
- Role Binding.

## Custom Pod Autoscaler Operator

The Custom Pod Autoscaler Operator (CPAO) would allow for quick and easy
creation of CPAs, taking in a Kubernetes custom resource description of the CPA
and provisioning all required Kubernetes resources to get it running and allow
it to interact with the parts of the cluster it needs. The CPAO uses a
Kubernetes controller to handle the actual implementation and logic of
provisioning the required resources. Kubernetes documentation describes the
combining of the custom resource and controller as part of the Operator pattern
- and there is a framework called the Operator Framework designed for this end.
The Operator Framework provides an SDK for developing operators. Implementation
of these would allow for a smooth process for creating custom scalers and
deploying them to clusters, allowing custom scaling logic and easy metric
gathering with little overhead.

The Custom Pod Autoscaler Controller would be written in Go using the Operator 
SDK by me as part of this Project. It would be distributed as a Docker image.

### Custom Pod Autoscaler Custom Resource

A custom resource in Kubernetes is an extension of the Kubernetes API that 
allows a short hand for quickly installing/deploying resources. CPAs would be 
set up as a custom resource on the cluster. The custom resource would allow 
users to define a CPA in a concise way, allowing for quick and easy install. 
The Custom Pod Autoscaler Custom Resource would be defined by me in YAML and 
provided as part of the process for installing a CPAO.

### Custom Pod Autoscaler Controller

A controller in Kubernetes is the implementation of the custom resource API, 
allowing logic to be written for creation/updating/deleting custom resources. 
Paired with the idea that the CPA is a custom resource would be the use of a 
controller in Kubernetes to allow implementation of logic for managing CPAs.  

The controller would handle provisioning the following:

- A single pod deployment to run the CPA in.
- A service account for the CPA to use when interacting with the Kubernetes API.
- A role binding describing the required API access for the CPA.
- A role to tie the service account to the role binding.
- Deploying these to the correct namespace.

### Kubernetes Resources

The Custom Pod Autoscaler Operator would require the following Kubernetes 
resouces:

- A role/cluster role to define permissions required by the operator.
  * Ability to get/create/delete/update service accounts.
  * Ability to get/create/delete/update deployments.
  * Ability to get/create/delete/update role bindings.
  * Ability to get/create/delete/update roles.
  * Ability to get/create/delete/update custom pod autoscaler custom resources.
- A service account for the operator to use.
- A role binding/cluster role binding to tie the role/cluster role to the 
service account.
- A deployment to run the operator controller inside.

These would be defined by me in YAML as part of the operator deployment bundle.

# Implementation

Both the Base and Operator should be implemented in a maintainable, testable 
and scalable way. With these three principles in mind the decisions around 
language, libraries and frameworks were made.

## Language

The Base and Operator were created using the 'Golang' programming language.  

One of the key benefits of building the application in Golang and distributing 
it as an open source codebase is that other applications can use the Custom Pod 
Autoscaler source code as a library import, and directly use Custom Pod 
Autoscaler structs, methods and interfaces.  

This would be useful for people developing autoscalers in Golang, as they could 
directly use structs for marshalling/unmarshalling from JSON to ensure 
compatibility with whichever version of the Custom Pod Autoscaler they are 
targeting.

## Semantic Versioning

## Linting

## Custom Pod Autoscaler Base

### Libraries

The following key libraries were used to develop the Custom Pod Autoscaler Base:

* `golang/glog` - Leveled logging for Golang, allowing different verbosity 
levels, 
and severity levels (`Info`, `Warning`, `Error`, and `Fatal`).
* `k8s.io/client-go` - Kubernetes API client for Golang, allowing interaction 
with the Kubernetes API. 
* `go-chi/chi` - Router for building Golang HTTP services.

### Docker

## Custom Pod Autoscaler Framework

### Libraries



# Testing

## Continuous Integration Pipeline

## Custom Pod Autoscaler Base

### Unit Tests

### Manual Testing

## Custom Pod Autoscaler Operator

### Unit Tests

### Manual Testing



# Evaluation

## Predictive Horizontal Pod Autoscaler (PHPA) comparision with Horizontal Pod Autoscaler (HPA) for seasonal loads 

### Overview

Aiming to validate the utility of the Predictive Horizontal Pod Autoscaler (HPA)
for autoscaling a Kubernetes cluster with realistic data this experiment was
created to provide a suitable comparison with the existing Kubernetes Horizontal
Pod Autoscaler (PHPA).

The experiment will involve both autoscalers managing an application that will
experience varied levels of load. The experiment will seek to evaluate
performance of the autoscalers in managing these applications; with latency
results being used to determine effectiveness. Everything should be kept the
same between the two autoscalers - they will both manage the same application,
and the load will be managed by the same load testing logic. 

Each test will have have three elements, the autoscaler, an application to
manage, and the load testing application. The autoscaler will be the only part
that changes. The application will be a simple example web server that responds
`OK!` to `GET` at path `/`; it is the `k8s.gcr.io/hpa-example` that is used in
Kubernetes autoscaling walkthroughs. The load testing application will be a
python script that will invoke Locust load testing at set intervals, varying the
load applied based on the time of day. The load testing will also periodically
record how many replicas the deployment has. Figure \ref{phpa_long_phpa_diagram}
shows the experiment overview for the PHPA, while figure
\ref{phpa_long_hpa_diagram} shows the experiment overview for the HPA.


This experiment will run for 3 days and is designed to have the PHPA and HPA 
running in their own clusters. 

![Predictive Horizontal Pod Autoscaler Experiment\label{phpa_long_phpa_diagram}][phpa_long_diagram_hpa_design] 

![K8s Horizontal Pod Autoscaler Experiment\label{phpa_long_hpa_diagram}][phpa_long_diagram_phpa_design] 

The load applied will be the same for each autoscaler;

- High load (40 users) will be applied between 15:00 and 17:00.
- Medium load (25 users) will be applied between 9:00 and 12:00.
- Low load (15 users) will be applied for all other times.

The Horizontal Pod Autoscaler will be configured with the following options:

- Minimum replicas: `1`.
- Maximum replicas: `20`.
- Sync Period (`--horizontal-pod-autoscaler-sync-period`): `15s` (default).
- Downscale Stabilization 
(`--horizontal-pod-autoscaler-downscale-stabilization`): `5m` (default).
- Tolerance (`--horizontal-pod-autoscaler-tolerance`): `0.1` (default).
- CPU Initialization Period 
(`--horizontal-pod-autoscaler-cpu-initialization-period`): `5m` (default).
- Initial Readiness Delay 
(`--horizontal-pod-autoscaler-initial-readiness-delay`): `30s` (default).
- Metrics: Resource metric targeting CPU usage, with average utilization at 
`50`.

The Predictive Horizontal Pod Autoscaler will have the same settings as the 
Horizontal Pod Autoscaler:

- Minimum replicas: `1`.
- Maximum replicas: `20`.
- Sync Period (`--horizontal-pod-autoscaler-sync-period`): `15` (seconds, same
  as HPA `15s`) (default).
- Downscale Stabilization 
(`--horizontal-pod-autoscaler-downscale-stabilization`): `300` (seconds, same
  as HPA `5m`) (default).
- Tolerance (`--horizontal-pod-autoscaler-tolerance`): `0.1` (default).
- CPU Initialization Period 
(`--horizontal-pod-autoscaler-cpu-initialization-period`): `300` (seconds, same
  as HPA `5m`) (default).
- Initial Readiness Delay 
(`--horizontal-pod-autoscaler-initial-readiness-delay`): `30` (seconds, same
  as HPA `30s`) (default).
- Metrics: Resource metric targeting CPU usage, with average utilization at 
`50`.

The Predictive Horizontal Pod Autoscaler will also have the following 
configuration settings for tuning the Holt-Winters algorithm:

- Model Holt-Winters
  * Per Interval: `1` (Run every interval)
  * Alpha: `0.1`
  * Beta: `0.1`
  * Gamma: `0.9`
  * Season Length: `5760` (24 hours in 15 second intervals)
  * Stored Seasons: `4` (store last 4 days data)
  * Method: `additive`

### Hypothesis

The Predictive Horizontal Pod Autoscaler using the Holt-Winters prediction
method will pre-emptively scale compared to the standard Kubernetes Horizontal
Pod Autoscaler which will only retroactively react. This will be manifested in
higher replica counts when scaling up, and scaling up earlier; with the result
of lower average and maximum latency, and less failed requests - primarily
around the moment of change from lower load levels to high load. This effect
will only be apparant after at least one full season (24 hours); for the
first season as the predictor won't have data to make a prediction therefore it
is expected to have approximately the same performance as the standard
Kubernetes Horizontal Pod Autoscaler.

### Results
Figure \ref{phpa_rep_compare} displays how the replica count varies with the
changes in request numbers to the application, and how the replica count is
predictable and repeatable daily.  

From figure \ref{phpa_rep_compare} it is clear when the PHPA's predictive
element comes into effect, after the start of day 2.

Looking at the average latency (figure \ref{phpa_avg_compare}), it appears that
my hypothesis is confirmed - the PHPA acted proactively and predicted increases
in load; resulting in less spikes in average latency. Taking a more detailed
look into the results it further confirms this hypothesis. 

Figure \ref{phpa_avg_compare_1} shows the first day, in which the HPA and PHPA
have similar average latencies in response to the number of requests; with both
having a sharp peak on the increase from low load to high load. 

Figure \ref{phpa_avg_compare_2} shows the second day, when the predictive
element of the PHPA will start being used to make predictions. The PHPA does not
result in the same average latency spike as the HPA does transitioning from both
low to medium loads, and low to high loads. This shows that the predictive
element proactively scaled to better meet upcoming demand.

Figure \ref{phpa_avg_compare_3} shows the third day, which follows the same
liness as the second day, with peaks in average latency eliminated by the PHPA.

Figures \ref{phpa_max_compare_1} and \ref{phpa_max_compare_2} fit my hypothesis,
with the first day seeing a similar maximum latency performance between the HPA
and the PHPA, before seeing a reduction in maximum latency spikes in the second day.

The maximum latency, shown in \ref{phpa_max_compare}, reveals a possible
limitation and complication of applying the predictive model - as the season
experiment progressed, in the third day, there were some large spikes in maximum
latency for the PHPA, figure \ref{phpa_max_compare_3} shows this in more detail.
It appears that as the experiment progressed the replica count became more
erratic, which could be the cause for these latency spikes. This erratic
rescaling I believe is caused by the statistical model applied during the
experiment being poorly tuned, placing a heavy emphasis only on seasonal data,
causing previous natural fluctuations in replica counts to be exaggerated. This
fluctation due to tuning should be investigated closely if the PHPA was to be
used in a production environment.  

![Replica comparison\label{phpa_rep_compare}][phpa_long_replicas]

![Average latency comparison\label{phpa_avg_compare}][phpa_long_avg_latency]

![Average latency comparison for day 1\label{phpa_avg_compare_1}][phpa_long_avg_day_1_latency]

![Average latency comparison for day 2\label{phpa_avg_compare_2}][phpa_long_avg_day_2_latency]

![Average latency comparison for day 3\label{phpa_avg_compare_3}][phpa_long_avg_day_3_latency]

![Maximum latency comparison\label{phpa_max_compare}][phpa_long_max_latency]

![Maximum latency comparison for day 1\label{phpa_max_compare_1}][phpa_long_max_day_1_latency]

![Maximum latency comparison for day 2\label{phpa_max_compare_2}][phpa_long_max_day_2_latency]

![Maximum latency comparison for day 3\label{phpa_max_compare_3}][phpa_long_max_day_3_latency]

### Conclusion

The PHPA outperforms the HPA in reduction of average latency spikes due to
increased load for seasonal data. The PHPA provides a valuable tool for
proactive autoscaling, and if applied to regular, predictable and repeating user
loads it can provide a more effective autoscaling solution than the standard
Kubernetes HPA. However, the key to effective use of the PHPA is that it needs
to be data driven, and as such requires tuning to be effective and useful. The
PHPA should be applied in specific circumstances in which it makes sense; the
decision to apply it should be driven by an understanding of the system it is
being applied to and it should be backed with data to allow for better tuning
and a more useful autoscaling solution; otherwise unwanted results such as
erratic scaling behaviour may arise out of poor tuning decisions.

## LPA comparison with HPA for high CPU usage application

### Overview

### Hypothesis

### Results

### Conclusion

## Autoscaling based on Twitter activity

### Overview

### Conclusion

## HPA running as CPA comparison with Kubernetes HPA

### Overview

### Conclusion

## Game Server Scaling

### Overview

### Conclusion


[phpa_long_diagram_hpa_design]:
predictive-horizontal-pod-autoscaler/long/diagrams/PHPA_long_experiment_k8s_hpa_design.svg
[phpa_long_diagram_phpa_design]:
predictive-horizontal-pod-autoscaler/long/diagrams/PHPA_long_experiment_k8s_hpa_design.svg
[phpa_long_replicas]:
predictive-horizontal-pod-autoscaler/long/results/replica_compare.svg
[phpa_long_avg_latency]:
predictive-horizontal-pod-autoscaler/long/results/avg_latency_compare.svg
[phpa_long_avg_day_1_latency]:
predictive-horizontal-pod-autoscaler/long/results/avg_latency_day_1.svg
[phpa_long_avg_day_2_latency]:
predictive-horizontal-pod-autoscaler/long/results/avg_latency_day_2.svg
[phpa_long_avg_day_3_latency]:
predictive-horizontal-pod-autoscaler/long/results/avg_latency_day_3.svg
[phpa_long_max_latency]:
predictive-horizontal-pod-autoscaler/long/results/max_latency_compare.svg
[phpa_long_max_day_1_latency]:
predictive-horizontal-pod-autoscaler/long/results/max_latency_day_1.svg
[phpa_long_max_day_2_latency]:
predictive-horizontal-pod-autoscaler/long/results/max_latency_day_2.svg
[phpa_long_max_day_3_latency]:
predictive-horizontal-pod-autoscaler/long/results/max_latency_day_3.svg