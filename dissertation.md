---
title: Kubernetes Custom Autoscaling
author: Jamie Thompson
date: 24/04/2020
---

# Introduction

Kubernetes (K8s) in its current state allows setting how many pods a deployment has, 
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

## Custom Pod Autoscaler Framework (CPAF)

The Custom Pod Autoscaler Framework (CPAF) is a combination of systems for
the creation, management and running of Custom Pod Autoscalers (CPA). A Custom
Pod Autoscaler is a single docker image that manages a deployment, handling
scaling. It is responsible for gathering metrics, making evaluations and
interacting with Kubernetes to scale the deployments it manages.

The CPAF is split up into two distinct parts, Custom Pod Autoscalers and
the Custom Pod Autoscaler Operator (CPAO). The Custom Pod Autoscaler is further
split into two parts, the Custom Pod Autoscaler Base (CPAB) and User Defined
Logic (UDL). See figure \ref{cpaf} for an overview.  

![Custom Pod Autoscaler Framework Overview\label{cpaf}](assets/design/cpaf.svg)

### Custom Pod Autoscaler Base (CPAB)

The Custom Pod Autoscaler Base (CPAB) is be a program that handles all
complexities when interacting with Kubernetes and the API. This program provides
a base for users to write their own logic on top of, while abstracting away much
of the complexity. The program is highly configurable. See figure \ref{cpab} for
an overview.  

The CPAB is be built by me as part of this project. The CPAB would be 
distributed as both a binary and built into a set of Docker images.

![Custom Pod Autoscaler Base Architecture
Overview\label{cpab}](assets/design/cpab_architecture.svg)

#### Scaler

The Scaler is part of the CPAB responsible for interfacing with the Kubernetes
API. This part is able to take in a target replica count and a K8s resource
details and then interface with the K8s API to cause the resource to scale to
the target replica count provided. This uses standard Kubernetes scaling
endpoints for setting replica counts.

#### Metric Gatherer

The Metric Gatherer is part of the CPAB responsible for reaching out to the UDL
to gather metrics. The Metric Gatherer takes input information about the
resource being managed and then feeds this into the UDL responsible for metric
gathering configured by the developer of the CPA. The Metric Gatherer then
parses the output from the UDL, catches any errors, and then returns the metrics
retrieved from the UDL.

#### Evaluator

The Evaluator is part of the CPAB responsible for reaching out to the UDLto make
decisions on how to scale the resource being managed. The Evaluator takes as
input metrics that have been gathered by the Metric Gatherer; and then feeds
this into the UDL responsible for evaluating metrics configured by the developer
of the CPA. The Evaluator then parses the output from the UDL, catches any
errors, and then returns evaluations retrieved from the UDL.

#### Autoscaler

The Autoscaler part of the CPAB program handles the actual scaling mechanism.
This part is responsible for interacting with the Kubernetes API and retriving
relevant information about the resource being managed, before feeding this into
the user defined logic to gather metrics and retrieve evaluations. The
autoscaler then takes these decisions from the user defined logic and uses them
to interact with the Kubernetes API to scale the resources being managed. See
figure \ref{autoscaler_overview} for an overview of the autoscaler's flow.  

The Autoscaler runs repeatedly at a set interval, gathering metrics, evaluating
and then scaling. This repeated process runs concurrently to the rest of the
application, without blocking any other part of the program.  

The Autoscaler fails safely; if user defined logic fails or crashes, or if the
autoscaler itself fails or crashs, it does not affect the resource being
managed. If the autoscaler crashes or fails, scaling does not occur; scaling
only occurs if the autoscaler processes all user defined logic and calculates an
evaluation correctly and without errors.  

![Autoscaler Logic Flow\label{autoscaler_overview}](assets/design/autoscaler_overview.svg)

#### HTTP REST API

The CPAB exposes a HTTP REST API for runtime interactions with the CPA. The API
allows triggering the autoscaler through a HTTP request, retrieving metrics
without evaluating, and retrieving evaluations without scaling as part of a dry
run.  

This API allows the CPA to be integrated as part of a wider system and allow for
manual control over the autoscaler.  

The REST API is versioned to ensure compatiblity across new versions, starting
at API version `v1`. This is usable as `/api/<VERSION>/endpoint` to prevent
breaking API changes from disrupting systems/workflows.

##### HTTP REST API v1
###### Get Metrics

**URL** : `/api/v1/metrics`

**Method** : `GET`

Used to run metric gathering and return the results.

###### Create Evaluation

**URL** : `/api/v1/evaluation`

**Method** : `POST`

Used to evaluate metrics and then scale based on them.

#### Configuration Options

Configuration for the CPA is available at both build time and deploy time. This
configuration is provided through either a YAML configuration file that is built
into the Docker image at build time, or through environment variables injected
into the Docker container at runtime. Both configurations are usable at the same
time, with runtime configuration taking precedence and overwriting the build
time configuration.  

The following options are be configurable:

- The path to the configuration file (through an environment variable only).
- The interval between autoscaling.
- The namespace of the resource being managed.
- Minimum replica target.
- Maximum replica target.
- The start time of the autoscaler, from this time the interval will be
  calculated, allowing the autoscaler to sync up with certain timings, such as
  running every 5 minutes starting exactly from the hour (e.g. 15:00, 15:05,
  15:10 etc.)
- How verbose the CPAB logs are.
- API configuration options.
  - Enable/disable the API.
  - Use HTTP/HTTPS for the API.
  - API port.
  - API host.
  - API certificate.
  - API private key.
- Downscale stabilization - this is a feature of the K8s HPA, allows a cooldown
  for downscaling to avoid thrashing; defines a time period and then only allows
  the autoscaler to scale to the maximum evaluation over this time period.

#### Methods

UDL is accessed and triggered through an abstraction called *Methods*, which are
configurable ways to call and interact with User Defined Logic. A *Method* is
specified in configuration, and this abstraction allows for different ways of
interacting with UDL to be available; while also allowing future additions of
new ways to interact in a non-breaking and consistent way.  

Each method has a clear specification to allow developers to fully understand
and utilise the framework, without running into issues around lack of
consistency or clarity.  

A method's input and output are be context based, requiring each possible
context that the method is called in to be fully specified and documented to
allow for a better developer experience.  

Each method has a timeout configuration option, allowing automatic timing out of
the method if it takes longer than the method logic will exit and a timeout
error will occur.

##### Shell Method

The Shell Method allows interaction through a shell command and the Unix pipe
system. This woulds developers to create their UDL in a flexible way, supporting
any language and framework the developer wants to use (Python, Golang, Java
etc.) - the only requirement is it must be startable by a shell command.  

The Shell Method is specified by providing the following:

- An entrypoint for the shell command, for example `/bin/bash`.
- The command to execute, for example `python script.py`.

##### HTTP Method

The HTTP Method allows interaction through HTTP calls. This allows developers to
expose an API for the CPAB to call, and their UDL could run anywhere - within
the CPA Pod, another Pod in the Kubernetes cluster, or even outside of the
Kubernetes cluster. The only requirement for this is that it must expose HTTP
endpoints that can recieve and respond to HTTP calls.  

The HTTP Method is specified by providing the following:

- An HTTP Method for the call, such as `GET` or `POST`.
- A URL to specify the endpoint to call, for example `https://0.0.0.0:5000/metrics`.
- A set of HTTP headers that can be provided with the call.
- A choice of parameter method, allowing data to be transferred either through a
  query parameter or a body parameter.


### User Defined Logic (UDL)

User Defined Logic (UDL) is the customised programs written by developer
users of the CPA. The UDL is split into two parts, metric gathering and
evaluations.  

UDL could exist either inside the Docker container, for example as a Python
script that is started by a shell command (see figure \ref{cpab_docker_inside});
or it could exist outside of the Docker container, for example as a service that
exposes a HTTP REST API (see figure \ref{cpab_docker_outside}).  

All UDL is be able to produce errors and halt CPA execution by raising errors in
the standard way for the method used to call it, for example if using a shell
method a non-zero exit code represents an error and stop execution.

![Custom Pod Autoscaler UDL inside Docker Container
overview\label{cpab_docker_inside}](assets/design/cpab_docker_inside.svg)

![Custom Pod Autoscaler UDL outside Docker Container
overview\label{cpab_docker_outside}](assets/design/cpab_docker_outside.svg)

#### Metric Gathering

Metric Gathering UDL takes in information about the resource being managed, such
as a full deployment description and specification, or a full pod description
and specification. This input information has to be in a parsable and consistent
format, such as JSON or YAML. The Metric Gathering UDL then runs it's own
calculations and logic, defined by the CPA developer user, before returning any
calculated/gathered metrics in JSON.

#### Evaluating

Evaluating Gathering UDL takes in gathered metric information. This input
information has to be in a parsable and consistent format, such as JSON or YAML.
The Evaluating UDL then runs it's own calculations and logic, defined by the CPA
developer user, before returning any calculated evaluations in JSON.

#### Hooks

The CPA exposes a series of hooks for injecting further customisation:

- Before metric gathering, given metric gathering input.
- After metric gathering, given metric gathering input and result.
- Before evaluation, given evaluation input.
- After evaluation, given evaluation input and result.
- Before scaling decision, given min and max replicas, current replicas, target
  replicas, and resource being scaled.
- Before scaling decision, given min and max replicas, current replicas, target
  replicas, and resource being scaled. 

### Kubernetes Resources

Running the CPA in a Kubernetes cluster requires some configuration in the
cluster. The CPA requires a single pod deployment to run in; Kubernetes manages
this deployment. Further configuration is also required to allow the CPA to
interact with deployments and pods in the cluster; requiring a Service Account,
a Role and a Role Binding. This could be manually set up by the user, but could
be difficult to set up and time consuming, to address this an operator is
offered to allow easy install.  

Required Resources:  

- Deployment.
- Service Account.
- Role.
- Role Binding.

### Custom Pod Autoscaler Operator

The Custom Pod Autoscaler Operator (CPAO) allows for quick and easy creation of
CPAs, taking in a Kubernetes custom resource description of the CPA and
provisioning all required Kubernetes resources to get it running and allow it to
interact with the parts of the cluster it needs. See figure \ref{cpao_overview}
for an overview the CPAO.

The Custom Pod Autoscaler Controller is distributed as a Docker image.

![Custom Pod Autoscaler Operator
overview\label{cpao_overview}](assets/design/cpao_overview.svg)

#### Custom Pod Autoscaler Custom Resource

A custom resource in Kubernetes is an extension of the Kubernetes API that
allows a short hand for quickly installing/deploying resources. CPAs are set up
as a custom resource on the cluster. The custom resource allows users to define
a CPA in a concise way, allowing for quick and easy install. 

#### Custom Pod Autoscaler Controller

A controller in Kubernetes is the implementation of the custom resource API, 
allowing logic to be written for creation/updating/deleting custom resources. 
Paired with the idea that the CPA is a custom resource is the use of a
controller in Kubernetes to allow implementation of logic for managing CPAs.  

The controller handles provisioning the following:

- A single pod deployment to run the CPA in.
- A service account for the CPA to use when interacting with the Kubernetes API.
- A role binding describing the required API access for the CPA.
- A role to tie the service account to the role binding.
- Deploying these to the correct namespace.

The Controller is also be responsible for reading in configuration included in
the CPA custom resource and injecting this runtime configuration as environment
variables into the CPA Docker container.

#### Kubernetes Resources

The Custom Pod Autoscaler Operator requires the following Kubernetes 
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

## Locust Pod Autoscaler (LPA) comparison with Horizontal Pod Autoscaler (HPA) for high CPU usage application

### Overview

### Hypothesis

### Results

### Conclusion

## Autoscaling based on Twitter activity

### Overview

### Conclusion

## Horizontal Pod Autoscaler (HPA) running as Custom Pod Autoscaler (CPA) comparison with Kubernetes HPA

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