---
title: Kubernetes Custom Autoscaling
author: Jamie Thompson
date: 24/04/2020
header-left: 40178456
header-center: Kubernetes Custom Autoscaling
header-right: Jamie Thompson
float-placement-figure: p
titlepage: true
titlepage-color: "436ce5"
titlepage-text-color: "ffffff"
titlepage-rule-color: "ffffff"
toc-own-page: true
header-includes: |
  \RedeclareSectionCommands[
    afterskip=1.25ex plus .1ex
  ]{paragraph,subparagraph}
bibliography: bibliography.bib
citation-style: template/ieee.csl
numbersections: true
secnumdepth: 4
---

# Introduction

Kubernetes (K8s) is a container orchestration system, which allows sharing
compute resources between applications that run on it. K8s uses the abstractions
of *pods* and *resources* to represent these compute resources. A pod is
analogous to a container, while a resource is an application and the pods that
the application is running on.

K8s in its current state allows setting how many pods a resource has, allowing
you to set a target amount of pods it should have and K8s will reconcile this
and ensure that it reaches that target.  

K8s provides the *Horizontal Pod Autoscaler* (HPA) which allows automatic scaling
of the number of pods a resource has based on metrics that you feed into the
HPA. Generally these metrics are CPU/memory load of the pod, allowing scaling up
if the load gets too much or down if resources are underutilized; but also
includes custom metrics defined through the metrics API. The HPA takes these
metrics and applies a built in algorithm to them to determine the number of pods
to scale up/down. This process is called *autoscaling*.

## Problems

There are two problems in the current K8s HPA setup:

- Hard-coded algorithm with less flexibility.
- Custom metrics can be difficult to set up.

### Hard-coded Algorithm

The HPA built in algorithm is:

```
desiredReplicas = ceil[currentReplicas * ( currentMetricValue / desiredMetricValue )]
```
[@kubernetes_io_hpa]

The built in algorithm may not suit your needs; you may require more complex 
scaling logic. The only way to currently resolve this is to write your own 
scaler from scratch, which is a complex and difficult task - with an added 
vector of failure if there are bugs in your scaling. Writing this scaler 
requires an intimate understanding of K8s and its APIs.

### Custom Metrics Difficulty

Custom metrics requires the use of third party adapters (e.g. Prometheus, Sysdig
Monitor), or requires the user to write their own adapter. This requires a lot
of configuration, and in the case of writing their own adapter requires in-depth
K8s API knowledge. See figure \ref{sysdig_scaler_overview} for an example Sysdig
autoscaling system, and figure \ref{general_custom_metrics} for a generalised
system.

![Sysdig Custom Metrics autoscaling overview\label{sysdig_scaler_overview}
[@sysdig_custom_metrics]](assets/intro/sysdig_kubernetes_scaler_overview.png)

![General Custom Metrics autoscaling
overview\label{general_custom_metrics}](assets/intro/existing_k8s_metrics.svg)

## Users

There are three key users that are affected by the current problems with the
current Kubernetes autoscaling setup:

- Developer
- Cluster Administrator
- Consumer

There is overlap in these users, a user may fit both the Developer and Cluster
Administrator categories, or any mix of categories.

### Developer

The Developer is the user that builds custom autoscalers, the problem that
they face is that custom autoscalers are difficult and time consuming to create;
with an added overhead of testing, maintenance and responsibility for a complete
custom autoscaling system. The developer must have in-depth K8s knowledge to
develop the custom autoscaler, which is an investment of time and effort.

### Cluster Administrator

The Cluster Administrator is the user that is responsible for K8s cluster
operations, deploying autoscalers and determining which autoscaling metrics to
use. This user faces the issue that a complex HPA integration, using third party
adapters and tooling is complicated to configure and maintain. The complexity of
these autoscaling systems can make them brittle and easy to break. 

### Consumer

The Consumer is the user that accesses the application running on the K8s
cluster that is being managed by an autoscaler. The problems this user can face
is less responsive applications, or an increased cost in using the service; due
to lack of flexiblity in autoscaling solutions to manage compute resources.

## Existing Attempts at Solutions

### Horizontal Pod Autoscaler with Custom Metrics

Augmenting the HPA with *custom metrics* goes some way in addressing some of the
problems, granting greater flexibilty beyond standard K8s metrics such as CPU,
and memory use. Custom metrics are user-defined metrics, which can be generated
by other applications and integrated with standard K8s metrics. The custom
metrics approach allows supplying more data to the HPA to use for scaling,
allowing a the Cluster Administrator user greater control over the autoscaling process. 

This approach does not address all of the problems. This approach still relies
on the hard-coded HPA scaling algorithm, which can can make a scaling technique
using this very complex, or even ultimately could block a certain method
entirely. The custom metrics style of autoscaling has an added overhead in
complexity, with third-party adapters and applications required to generate,
collect and feed the custom metrics into the K8s metrics API. This requires more
maintenance, configuration and understanding of a variety of systems to augment
the K8s cluster.

### Agones Fleet Autoscaler

>Agones is a library for hosting, running and scaling dedicated game servers on
>Kubernetes. 
[@agones_overview]

Agones provides a custom autoscaler for the Agones game hosting K8s framework.
This autoscaler is called the *Fleet Autoscaler*, this autoscaler is designed to
scale game servers - allowing the use of a buffer based autoscaling strategy, or
a webhook driven strategy; allowing the injection of custom autoscaling logic.

Buffer based autoscaling works by ensuring that there are a minimum and maximum
number of available game servers; this is an alternative to autoscaling based on
other metrics such as CPU usage or memory, which would not make sense for a game
server.

The webhook driven autoscaling works by allowing users to deploy a web server to
respond to webhooks, and configuring the autoscaler to send HTTPS requests to
this web server to determine how to scale. The web server responds with a
standard response on how to scale the resource
[@agones_autoscaler_specification].

The Agones Fleet Autoscaler addresses many of the issues highlighted - providing
n alternative to the hard-coded autoscaling algorithm of the HPA through the
buffer and webhook driven autoscaling techniques. The webhook method provides
the ability to inject custom user written logic, exposed through an HTTP API.
This would allow a developer to create custom autoscaling, and allow a cluster
administrator to apply different scaling techniques.

The drawback of the Agones Fleet Autoscaler is that it is only available as part
of the Agones ecosystem. The autoscaler is not generalised and requires the use
of Agones abstractions such as *fleets*, which prevent it from being deployed on
a standard K8s cluster. If a user wanted to utilise this autoscaling technique,
they would be required to use the entire Agones framework - which is built
exclusively for game server hosting, and as such is not applicable to most
scenarios.

\newpage

# Solution

The Custom Pod Autoscaler Framework (CPAF) is designed to address these two 
problems. The CPAF would work by allowing the creation of Custom Pod 
Autoscalers (CPA) and letting them run inside a K8s cluster.  

The CPA would contain custom user defined logic for scaling, alongside a base 
program to handle interactions with K8s and triggering the user defined 
logic. The CPA would allow for very simple scaling code to be written, in a 
variety of languages and with different technologies, while hiding the 
complexities of K8s.

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
configuration, third party deployments or intricate K8s API knowledge.

### Creating a Custom Pod Autoscaler

CPAs should be extremely flexible in how they are created, supporting a wide 
variety of languages, frameworks, environments, and interfaces.

### Deploying a Custom Pod Autoscaler

CPAs should be deployed in the standard way to deploy to K8s, through 
K8s deployment YAML. This is flexible, and also has the benefit of 
including compatiblity with some other commonly used tools, such as Helm.  

Deploying through K8s YAML provides the benefit of familiarity and 
consistency with other parts of K8s; whilst also allowing more 
transparancy in versioning, resources used, and deploy time customisation.  

The deployment YAML should be as simple as possible, and without obscure or 
confusing resources included; much of the complexity should be abstracted away 
from the deploying user, whilst also retaining a level of customisation at 
deploy time. This could be achieved with a custom K8s resource and some 
logic in the form of a K8s controller or operator for managing the 
resource.  

Once a Custom Pod Autoscaler is deployed, it should be easy to interact with - 
it should provide a versioned HTTP REST API for retrieving information and for 
triggering autoscaling.

\newpage

# Requirements

## Must Have

- Can deploy a Docker image with autoscaling application into a K8s cluster.
  - Multiple distributed Docker images for various languages/environments.
    - Python Docker image.
    - Alpine Docker image.
- Autoscaler repeatedly runs.
- Supports user logic, can triggered through a shell command, allows
  specification in any language/framework that supports being called through
  shell commands. 
  - Supports HTTP requests from user logic.
- If user logic specifies that the number of replicas should change, scaling
  should occur and the number of pods should be adjusted. 
- \>= 70% Unit test coverage.
- Can be deployed with K8s YAML.
- K8s Custom Resource specifiying the Custom Pod Autoscaler to allow for simpler
  and easier deployment/configuration. 
- Syntax validation for Custom Pod Autoscaler K8s YAML.
- Deploying the K8s Custom Resource should provision all required K8s resources
  for the autoscaler. 
- Can deliver configuration options through K8s YAML.
- Can deliver configuration options through a supplied configuration file baked
  into the autoscaler image. 
- Configuration options.
  - How frequently the autoscaler runs.
  - Minimum and Maximum replicas
  - Which resource to target for scaling.
  - Timeouts for metric and evaluation gathering.
- Can delete the autoscaler.
  - Deletes all associated K8s resources.

## Should Have

- *Cooldown* feature to avoid *thrashing*.
  - Thrashing is when a resource is scaled up and down repeatedly in a short
    period of time, caused by being right on the threshold of an evaluation. For
    example, if the number of pods in a resource rapidly changes between 2 and
    3 because of small changes in the metrics as it is directly on a
    boundary/threshold.
  - Cooldown would allow defining a time period to gather metrics in and scale
    the highest value in that window. This would ensure that downscaling did not
    happen too quickly or erratically, and help smooth out the number of
    replicas over time.
- Allow choosing which pods to terminate when scaling down.
  - The CPA evaluator could decide which pods to terminate when scaling down,
    rather than relying on the Kubernetes decision making which bases it on how
    old the pod is.
  - This could be a list of pods with priorities assigned to them, with the
    lowest priority pods terminated when scaling down as needed.
- Manual triggering of the Custom Pod Autoscaler metric gathering and evaluation
  through an API.
  - Rather than being triggered just by the timer and at set intervals, the
    Custom Pod Autoscaler evaluation could be triggered manually, through a REST
    endpoint.
  - This would allow users to send an HTTP request to the Custom Pod Autoscaler
    and start an evaluation immediately, rather than waiting for the interval to
    expire.
  - Provide a *dry run* flag to the API to allow seeing how the autoscaler would
    scale without applying the results. 
- Hooks for different actions/stages in the autoscaling process.
  - Hooks would be points at which a user-defined shell command is executed, to
    allow users to have greater control of the Custom Pod Autoscaler. 
      - Before metric gathering.
      - After metric gathering.
      - Before evaluation.
      - After evaluation.
      - Before scaling.
      - After scaling.
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
- Full customisation of K8s resources, allowing Custom Pod Autoscalers to define
  their own resource dependencies. 
  - When this customised resource is provided, the Custom Pod Autoscaler should
    have ownership; meaning if the autoscaler is deleted the resource is
    deleted. 
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

\newpage

# Design

The Custom Pod Autoscaler Framework (CPAF) is a combination of systems for
the creation, management and running of Custom Pod Autoscalers (CPA) - with ease
of development, use, and configuration of K8s autoscalers as the primary
goal. A Custom Pod Autoscaler is a single docker image that manages a K8s
resource (such as a deployment) by handling scaling the resource up and down. It
is responsible for gathering metrics, making evaluations and interacting with
K8s to scale the resource it manages.

The CPAF is split up into two distinct parts, the Custom Pod Autoscaler and
the Custom Pod Autoscaler Operator (CPAO). The Custom Pod Autoscaler is further
split into two parts, the Custom Pod Autoscaler Base (CPAB) and User Defined
Logic (UDL). See figure \ref{cpaf} for an overview.  

![Custom Pod Autoscaler Framework Overview\label{cpaf}](assets/design/cpaf.svg)

## User Defined Logic

User Defined Logic (UDL) is the customised programs written by developer
users of the CPA. The UDL is split into two parts, metric gathering and
evaluations.  

UDL could exist either inside the Docker container, for example as a Python
script that is started by a shell command (see figure \ref{cpab_docker_inside});
or it could exist outside of the Docker container, for example as a service that
exposes a HTTP REST API (see figure \ref{cpab_docker_outside}).  

All UDL is able to produce errors and halt CPA execution by raising errors in a
standard way depending on the method used to call it, for example if using a
shell method a non-zero exit code represents an error and will stop execution.

![Custom Pod Autoscaler UDL inside Docker Container
overview\label{cpab_docker_inside}](assets/design/cpab_docker_inside.svg)

![Custom Pod Autoscaler UDL outside Docker Container
overview\label{cpab_docker_outside}](assets/design/cpab_docker_outside.svg)

### Metric Gathering

Metric Gathering UDL takes in information about the resource being managed, such
as a full deployment description and specification, or a full pod description
and specification. This input information has to be in a parsable and consistent
format, such as JSON or YAML. The Metric Gathering UDL then runs it's own
calculations and logic, defined by the CPA developer user, before returning any
calculated/gathered metrics in JSON.

### Evaluating

Evaluation UDL takes in gathered metric information. This input information has
to be in a parsable and consistent format, such as JSON or YAML. The Evaluating
UDL then runs it's own calculations and logic, defined by the CPA developer
user, before returning any calculated evaluations in JSON.

## Custom Pod Autoscaler Base

The Custom Pod Autoscaler Base (CPAB) is a program that handles all interactions
with K8s through its API. This program provides a base for users to write
their own logic on top of, while abstracting away much of the complexity. The
program is highly configurable.  

### Subsystems

The CPAB is structured as a collection of subsystems, with each subsystem
abstracting out a specific piece of functionality. These subsystems communicate
and interact together as a whole within the CPAB, see figure \ref{cpab} for an
overview. The CPAB is split into the following subsystems:

- Scaler
- Metric Gatherer
- Evaluator
- Autoscaler
- HTTP REST API

![Custom Pod Autoscaler Base Architecture
Overview\label{cpab}](assets/design/cpab_architecture.svg)

#### Scaler

The Scaler is part of the CPAB responsible for interfacing with the K8s
API. This part is able to take in a target replica count and a K8s resource
details and then interface with the K8s API to cause the resource to scale to
the target replica count provided. This uses standard K8s scaling
endpoints for setting replica counts.

The Scaler is part of the CPAB responsible for interfacing with the K8s API.
This part is provided a target replica count and the details of a K8s resource,
with this information it makes a request to the K8s Scaling API to target the
replica count provided. K8s will then apply its own processes and will scale the
resource to the target replica count if the cluster has capacity.

#### Metric Gatherer

The Metric Gatherer is the subsystem of the CPAB responsible for reaching out to
the UDL to gather metrics. The Metric Gatherer takes input information about the
resource being managed and then feeds this into the UDL responsible for metric
gathering configured by the developer of the CPA. The Metric Gatherer then
parses the output from the UDL, catches any errors, and then returns the metrics
retrieved from the UDL for other subsystems to use to make scaling decisions or
expose data through the CPAB API.

#### Evaluator

The Evaluator is the part of the CPAB responsible for interfacing with the UDL to
make decisions on how to scale the resource being managed. The Evaluator takes
as input metrics that have been gathered by the Metric Gatherer; and then feeds
this into the UDL responsible for evaluating metrics configured by the developer
of the CPA. The Evaluator then parses the output from the UDL, catches any
errors, and then returns evaluations retrieved from the UDL.

#### Autoscaler

The Autoscaler is the subsystem of the CPAB that handles repeatedly running at a
set interval, linking together the Metric Gatherer, Evaluator and Scaler
subsystems to automatically scale the resource at a defined interval.

The Autoscaler is the full automatic scaling pipeline, which operates repeatedly
on a configured schedule. The Autoscaler first calls the Metric Gatherer to
retrieve metrics, and then feeds these metrics into the Evaluator to retrieve an
evaluation, before finally sending this evaluation to the Scaler to scale the
resource through the K8s API. See figure \ref{autoscaler_overview} for an
overview of the autoscaler's flow.  

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

This API allows the CPAB to be controlled externally, either through an
automated process or manuall. This is highly useful, with the possibility of
automated control allowing integration of a CPA with a wider system. The ability
to manually control the CPAB is useful for development and testing of a CPA,
while also allowing administrators to have live control over the CPA.

The REST API is versioned to ensure compatiblity across new versions, starting
at API version `v1`. This is usable as `/api/<VERSION>/endpoint` to prevent
breaking API changes from disrupting systems/workflows.  

##### HTTP REST API v1

**Get Metrics**  
*Route* : `/api/v1/metrics`  
*Method* : `GET`  

Used to run metric gathering and return the results.

**Create Evaluation**  
*Route* : `/api/v1/evaluation`  
*Method* : `POST`  

Used to evaluate metrics and then scale based on them.

### Configuration Options

Configuration for the CPA is available at both container-build time and deploy
time. This configuration is provided through either a YAML configuration file
that is built into the Docker image at build time, or through environment
variables injected into the Docker container at runtime. Both configurations are
usable at the same time, with runtime configuration taking precedence and
overwriting the build time configuration.  

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
- Downscale stabilization - this is a reimplemented K8s HPA feature, allowing a
  cooldown for downscaling to avoid thrashing; defines a time period and then
  only allows the autoscaler to scale to the maximum evaluation over this time
  period.

### Methods

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

There are two available methods in the current CPAB:

- Shell Method
- HTTP Method

#### Shell Method

The Shell Method allows interaction through a shell command and the Unix pipe
system. This allows developers to create their UDL in a flexible way, supporting
any language and framework the developer wants to use (Python, Golang, Java
etc.) - the only requirement is it must be invokable by a shell command.  

The Shell Method is specified by providing the following:

- An entrypoint for the shell command, for example `/bin/bash`.
- The command to execute, for example `python script.py`.

#### HTTP Method

The HTTP Method allows interaction through HTTP calls. This allows developers to
expose an API for the CPAB to call, and their UDL could run anywhere - within
the CPA Pod, another Pod in the K8s cluster, or even outside of the
K8s cluster. The only requirement for this is that it must expose HTTP
endpoints that can recieve and respond to HTTP calls.  

The HTTP Method is specified by providing the following:

- An HTTP Method for the call, such as `GET` or `POST`.
- A URL to specify the endpoint to call, for example `https://127.0.0.1:5000/metrics`.
- A set of HTTP headers that can be provided with the call.
- A choice of parameter method, allowing data to be transferred either through a
  query parameter or a body parameter.

### Hooks

The CPA exposes a series of hooks for injecting further customisation:

- Before metric gathering, given metric gathering input.
- After metric gathering, given metric gathering input and result.
- Before evaluation, given evaluation input.
- After evaluation, given evaluation input and result.
- Before scaling decision, given min and max replicas, current replicas, target
  replicas, and resource being scaled.
- After scaling decision, given min and max replicas, current replicas, target
  replicas, and resource being scaled. 

### Kubernetes Resources

Running the CPA in a K8s cluster requires some configuration in the
cluster. The CPA requires a single pod deployment to run in; K8s manages
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

## Custom Pod Autoscaler Operator

The Custom Pod Autoscaler Operator (CPAO) allows for quick and easy creation of
CPAs, taking in a K8s custom resource description of the CPA and
provisioning all required K8s resources to get it running and allow it to
interact with the parts of the cluster it needs. See figure \ref{cpao_overview}
for an overview the CPAO.

![Custom Pod Autoscaler Operator
overview\label{cpao_overview}](assets/design/cpao_overview.svg)

### Custom Pod Autoscaler Custom Resource

A custom resource in K8s is an extension of the K8s API that
allows a short hand for quickly installing/deploying resources. CPAs are set up
as a custom resource on the cluster. The custom resource allows users to define
a CPA in a concise way, allowing for quick and easy install. 

### Custom Pod Autoscaler Controller

A controller in K8s is the implementation of the custom resource API, 
allowing logic to be written for creation/updating/deleting custom resources. 
Paired with the idea that the CPA is a custom resource is the use of a
controller in K8s to allow implementation of logic for managing CPAs.  

The controller handles provisioning the following:

- A single pod deployment to run the CPA in.
- A service account for the CPA to use when interacting with the K8s API.
- A role binding describing the required API access for the CPA.
- A role to tie the service account to the role binding.
- Deploying these to the correct namespace.

The Controller is also be responsible for reading in configuration included in
the CPA custom resource and injecting this runtime configuration as environment
variables into the CPA Docker container.

### Kubernetes Resources

The Custom Pod Autoscaler Operator requires the following K8s 
resouces:

- A role/cluster role to define permissions required by the operator.
  - Ability to get/create/delete/update service accounts.
  - Ability to get/create/delete/update deployments.
  - Ability to get/create/delete/update role bindings.
  - Ability to get/create/delete/update roles.
  - Ability to get/create/delete/update custom pod autoscaler custom resources.
- A service account for the operator to use.
- A role binding/cluster role binding to tie the role/cluster role to the 
service account.
- A deployment to run the operator controller inside.

\newpage

# Implementation

Both the CPAB and CPAO are implemented with three key principles in mind;
maintainability, testability and scalability. With these three principles in
mind the decisions around language, libraries and frameworks were made.

## Language

The CPAB and CPAO were created using the 'Golang' (or 'Go' for short)
programming language, version `1.13`.

### Simplicity

Go is an open source programming language designed with simplicity as a key aim
of the language. 'Go attempts to reduce the amount of typing in both senses of
the word. Throughout its design, we have tried to reduce clutter and
complexity.' [@golang_faq] This simplicity is enforced through a rigid and
restrictive syntax and code format, which ensures consistency in Go code. This
simplicity and consistency helps keep this project maintainable and approachable
for any developer that is familiar with Go.

### Concurrency

Go is designed with concurrency as a first class feature - '... the rise of
multicore CPUs argued that a language should provide first-class support for
some sort of concurrency or parallelism...' [@golang_faq] - which is useful in
this project for building a scalable HTTP REST API, alongside providing a
non-blocking concurrency solution for repeatedly running a timed autoscaler
alongside the API. 

### Interfaces

Go provides implicit interfaces, allowing interfaces to be defined where they
are consumed; with any structure that fulfils the interface contract to be
accepted as an interface of that type. This is highly useful for testing,
allowing easy stubbing of dependency behaviour, even when using third party
libraries that provide no interfaces.

### Application as a library

One of the key benefits of building the application in Go and distributing it as
an open source codebase is that other applications can use the Custom Pod
Autoscaler source code as a library import, and directly use Custom Pod
Autoscaler structs, methods and interfaces.  

This project has been developed with this understanding that the application
code will not only be used for building the executable, but also exposed as a
library for use by other developers when building their integrations and UDL for
a Custom Pod Autoscaler.  

### Go Modules

The version of Go used provides the *Go Modules* feature, with complete Golang
dependencies described by a Go module file `go.mod` and a checksum file
`go.sum`. This allows completely reproducible builds, while also providing ease
of use for developers, as they can add, remove and update dependencies through
the Go command line program. This go module feature allows a new developer to
join the project and retrieve all dependencies easily and reliably - reducing
set up time and difficulty.

### Widely Used in Kubernetes Ecosystem

Go is extensively used in the K8s ecoystem, with the K8s main project itself
written in Go, alongside a number of major libraries such as Helm, the Operator
Framework and Prometheus integrations. The widespread use of Go in the K8s
ecosystem has led to a strong community of Go developers, with a large amount of
documentation, tooling, and support. The K8s API provides direct support for Go
with the distribution of the `k8s.io/client-go` API client, providing a standard
toolset for interacting with the K8s API.

## Semantic Versioning

Both the CPAB and CPAO are versioned using Semantic Versioning - allowing users
to safely make decisions on upgrading to new versions. This versioning system
not only applies to the distributed executables and Docker images, but also to
the Go code importable as a library for developers.  

The core principles of Semantic Versioning are:

> Given a version number MAJOR.MINOR.PATCH, increment the:  
>
> 1. MAJOR version when you make incompatible API changes,
> 2. MINOR version when you add functionality in a backwards compatible manner, and
> 3. PATCH version when you make backwards compatible bug fixes.  
> Additional labels for pre-release and build metadata are available as
> extensions to the MAJOR.MINOR.PATCH format. [@semantic_versioning]


Beyond these principles, for initial development an unstable API is presented;
'Major version zero (0.y.z) is for initial development. Anything MAY change at
any time. The public API SHOULD NOT be considered stable.' [@semantic_versioning] Therefore until
`v1.0.0` is cut, the API for both the CPAB and CPAO is considered unstable.

### Changelog

Both the CPAB and CPAO have changes tracked through a changelog, which documents
all changes between versions. The changelog is formatted according to the 'Keep
a Changelog' changelog style. The maintenance of this changelog allows users to
see changes between versions, and make informed decisions on upgrading - while
also providing a utility for developers for tracking changes between versions.

> What is a changelog?
> A changelog is a file which contains a curated, chronologically ordered list
> of notable changes for each version of a project. 
>
> Why keep a changelog?
> To make it easier for users and contributors to see precisely what notable
> changes have been made between each release (or version) of the project.
> [@keep_a_changelog]

## Git Version Control

The CPAB and CPAO both use Git for version control, allowing collaboration and
change tracking. The projects are available as open source repositories on
GitHub, with issue tracking through GitHub issues and GitHub projects. This
public Git repository allows collaboration and community driven development,
with this transparency helping identify bugs and provide useful features.

## Linting

Both the CPAB and CPAO codebases are linted (static code analysis checking)
using Golint. This linting process is automated as part of the Continous
Integration pipeline and can be run locally by developers before pushing their
changes. This linting process helps ensure the codebase is consistent, clear,
and idiomatic - which ultimately helps the project remain maintainable.

## Documentation as Code

The two codebases are extensively documented using a *Documetation as Code*
approach, with documentation stored as markdown in the codebase. This markdown
documentation is in a wiki format, using `mkdocs` to generate HTML and host the
documentation locally. When the codebase on GitHub is updated, a service called
`readthedocs` generates HTML documentation from this markdown and publishes it
online.  

This *Documentation as Code* approach leads to a more up to date documentation
set; as a new feature, fix or change is implemented the documentation is updated
in the same commit by the developer. Since the documentation is stored in the
same Git repository as the rest of the codebase the documentation is versioned
alongside the code - allowing viewing of documentation for older versions.

## Git Feature Branch Workflow

The CPAB and CPAO are developed using the *Git feature branch worflow*, in which
each feature is developed in a separate branch before being merged into the
`master` branch once all checks have passed. No development is done on the
`master` branch directly, ensuring that `master` contains a working, tested and
releasable codebase at all times.

## Custom Pod Autoscaler Base

### Libraries

The following Go libraries were used to develop the Custom Pod Autoscaler Base:

- `golang/glog` - Leveled logging for Golang, allowing different verbosity 
levels, and severity levels (`Info`, `Warning`, `Error`, and `Fatal`).
- `k8s.io/client-go`, `k8s.io/api`, and `k8s.io/apimachinery` - K8s API
  client and structures for Golang, allowing interaction with the K8s
  API. 
- `go-chi/chi` - Router for building Golang HTTP services.
- `google/go-cmp` - Deep equality comparisons for testing.

### Distribution

#### Docker

Docker is a foundational technology for K8s, it is a widely used
open source container runtime. The CPAB is distributed inside/as Docker images,
with a variety of images provided to allow better and more distributed language
support. The distributed Docker images are:

- `custompodautoscaler/alpine` - CPAB bundled in an alpine Docker image.
- `custompodautoscaler/python` - CPAB bundled in a Docker image with a Python 3
  environment.

#### Binary

The executable binary (Linux 64-Bit) for the CPAB is distributed through GitHub releases,
allowing the executable to be downloaded directly. Distributing the binary in
this fashion gives third-party developers flexiblity in how they use the CPAB,
and allows integration of the exectuable into custom Docker images.

## Custom Pod Autoscaler Operator

### Libraries

The following Go libraries were used to develop the Custom Pod Autoscaler Operator:

- `github.com/go-logr/logr` - Standard Operator logging.
- `github.com/go-openapi/spec` and `k8s.io/kube-openapi` - Generation of YAML
  specifications from Go code.
- `github.com/operator-framework/operator-sdk` - The Operator SDK.
- `k8s.io/client-go`, `k8s.io/api`, and `k8s.io/apimachinery` - K8s API
  client and structures for Golang, allowing interaction with the K8s
  API. 
- `sigs.k8s.io/controller-runtime` and `sigs.k8s.io/controller-tools` -
  Additional runtime functionality for the Operator controller.
- `google/go-cmp` - Deep equality comparisons for testing.

#### Operator Framework

> The Operator Framework is an open source toolkit to manage Kubernetes native
> applications, called Operators, in an effective, automated, and scalable way. 

The CPAO is built using the Operator Framework, which is designed to provide
higher level API abstractions and project scaffolding for creating a K8s
Operator. The Operator Framework allows development of the operator in an
idiomatic and consistent way, whilst providing much of the boilerplate for
development through the use of the Operator SDK.

#### Docker

The CPAO is distributed as a Docker image, allowing it to be easily pulled down
from the public Docker repository and directly deployed to K8s clusters.
The distributed Docker image is `custompodautoscaler/operator` - built on top of
the `ubi7/ubi-minimal` Red Hat Docker base image, as is standard with an
Operator Framework operator.

#### Deployment YAML

The CPAO offers bundles of K8s YAML for deploying the Operator easily to
a K8s cluster. There are two available installation types, either
cluster-scoped installation or namespace-scoped installation. The cluster-scoped
option installs the operator with access to the entire cluster, while the
namespace-scoped option installs the operator only with access to the namespace
targeted during install.  

Both installation types are simple and easy to install, with two separate
commands listed in the Git repo's markdown to install each option.

\newpage

# Testing

Both the CPAB and CPAO are designed to run as key parts of infrastructure for a
K8s cluster - requiring extensive testing. The key aims for the testing should
be that the software is able to produce scaling results under normal conditions,
and under failing conditions it should be able to handle errors and fail safely.
Confidence in meeting these two aims is essential for these projects, to allow
trust for them to be deployed to production environments and on K8s systems both
large and small.  

The use of semantic versioning in these projects also presents the aim of no
unexpected breaking changes, a testing strategy is vitally important for this to
allow users to confidently upgrade between versions without being concerned
about breaking systems. Thorough testing also prevents software regression with
new versions, with previously fixed bugs being reintroduced.

With these primary aims in mind the CPAB and CPAO testing strategies are designed.

## Unit Tests

Unit tests for the CPAB and CPAO are written in Go using the standard Go testing
library. The tests are structured in a table-driven testing style; which is a
convention in Go tests. Table-driven tests use the same testing procedure for a
test, but allow varying input and expected output in a table of subtests - this
allows for ease of adding new tests by adjusting input and expected output.  

Both projects have a requirement of at least 70% unit test coverage of both the
entire codebase and any new code being added, otherwise the build will fail.  

In the CPAB and CPAO a decision was made not to run unit tests against the main
function entry into the programs, instead the main method is tested through the
manual testing. The rationale behind this is that the main method is mostly code
initialisation and is not a modular, self-contained component that has clearly
defined inputs and outputs - testing this should be based on the behaviour of
the application. The main method is excluded from coverage calculations.

## Custom Pod Autoscaler Base

### Unit Test Coverage

The CPAB has unit test coverage of 95%.

### Manual Testing

#### Autoscaler with Failing User Defined Logic

This tests that the CPAB will handle failing UDL.

1. Create a CPA Docker image pointing at a Python script that will exit with a
   non-zero exit code.
2. Deploy the CPAO to the cluster.
3. Deploy the CPA to the cluster, alongside an application to manage.
4. Use `kubectl logs --follow <CPA_NAME>` to view the logs of the CPA.
5. Check that an appropriate error is logged, and the CPA itself does not
   crash/scale the resource being managed.

#### Autoscaler running in Per Resource Mode

This tests that the CPAB handles per resource mode correctly.

1. Deploy the CPAO to the cluster.
2. Deploy a modified `python-custom-autoscaler` example CPA, alongside the
   example `paulbouwer/hello-kubernetes:1.5` application to manage.
3. Use `kubectl exec -it python-custom-autoscaler` to gain shell access to the
   autoscaler container.
4. Ensure that the managed application is scaled to the `numPods` label provided
   in the `paulbouwer/hello-kubernetes:1.5` deployment YAML. Redeploy after
   changing this label value and ensure that the number of replicas is adjusted.

#### Autoscaler running in Per Pod Mode

This tests that the CPAB handles per pod mode correctly.

1. Deploy the CPAO to the cluster.
2. Deploy the `simple-pod-metrics-python` example CPA to the cluster, alongside
   the example `flask-metric` application to manage.
3. Use `kubectl logs --follow simple-pod-metrics-python` to view the logs of the CPA.
4. Use `kubectl exec -it <APPLICATION_POD_NAME>`, use `increment` and
   `decrement` commands inside the Docker container to adjust the Pod metrics.
5. Ensure that if the total available metric across all Pods being managed goes
   below 1 a new Pod is requested.
6. Ensure that if the total available metric accross all Pods being managed goes
   above 5 a Pod is terminated.

#### Autoscaler with API disabled

This tests that the CPAB disables the API if requested.

1. Deploy the CPAO to the cluster.
2. Deploy a modified `python-custom-autoscaler` example CPA, with the API enabled option
   set to false, to the cluster, alongside the example
   `paulbouwer/hello-kubernetes:1.5` application to manage.
3. Use `kubectl exec -it python-custom-autoscaler` to gain shell access to the
   autoscaler container.
4. Use the command `curl -X GET http://localhost:5000/api/v1/metrics`.
5. Ensure the response of this command is not successful, and a failed to
   connect error is displayed.

#### Autoscaler with HTTPS API

This tests the CPAB will host the API using correct SSL certificates if
provided.

1. Deploy the CPAO to the cluster.
2. Generate an SSL certificate and private key file.
3. Bundle these SSL certificates into a CPA Docker image, update configuration
   for HTTPS to point to the certificate and private key filepaths.
4. Deploy the CPA to the cluster.
5. Use `kubectl exec -it <CPA_POD_NAME>` to gain shell access to the autoscaler.
6. Use the command `curl -X GET http://localhost:5000/api/v1/metrics`.
7. Ensure the response of this command is not successful, and a failed to
   connect error is displayed.
8. Use the command `curl -k -X GET https://localhost:5000/api/v1/metrics`.
9. Ensure that there is a valid response from the server, with a `200 OK`
   message.

#### Autoscaler with No Configuration Provided

This tests the CPAB will provide an error and not run if no configuration is
provided.

1. Deploy the CPAO to the cluster.
2. Deploy an autoscaler with no configuration YAML file.
3. Check that the Pod is in state `Error`.
4. Use `kubectl logs <CPA_POD_NAME>` to see the error logs.
5. Ensure that the following error is logged: `Fail to read configuration file /config.yaml`.

#### Autoscaler Starting at a Full Minute

This tests that the CPAB will start its scheduled autoscaling at the correct
time, as specified by the `startTime` configuration option.

1. Deploy the CPAO to the cluster.
2. Deploy an autoscaler on a 30 second mark (for example 15:32:30, 17:32:30)
   with `startTime` configured as set to `60000`.
3. Check that the Pod is in state `Running`.
4. Use `kubectl logs <CPA_POD_NAME>` to see the logs.
5. Ensure that the logs report that the autoscaler is waiting ~30 seconds before
   starting to autoscale, starting to autoscaling only on the full minute.

## Custom Pod Autoscaler Operator

### Unit Test Coverage

The CPAO has unit test coverage of 98%.

### Manual Testing

#### Deploy Custom Pod Autoscaler Operator Namespace-wide

This tests that the CPAO can be deployed namespace wide on a cluster.

1. Run the following command to deploy to do a namespace deploy on the cluster:
```
NAMESPACE=<INSERT_NAMESPACE_HERE>
VERSION=<INSERT_VERSION_HERE>
kubectl config set-context --current --namespace=${NAMESPACE}
curl -L "https://github.com/jthomperoo/custom-pod-autoscaler-operator/releases/download/${VERSION}/namespace.tar.gz" | tar xvz --to-command 'kubectl apply -f -'
```
2. Ensure the following resources exist in the namespace provided.
  - A Deployment called ``.
  - A Pod called ``.
  - A Service Account called ``.
  - A Role called ``.
  - A RoleBinding called ``.

3. Ensure the Pod is running.

#### Deploy Custom Pod Autoscaler Operator Cluster-wide

This tests that the CPAO can be deployed namespace wide on a cluster.

1. Run the following command to deploy to do a namespace deploy on the cluster:
```
VERSION=<INSERT_VERSION_HERE>
curl -L "https://github.com/jthomperoo/custom-pod-autoscaler-operator/releases/download/${VERSION}/cluster.tar.gz" | tar xvz --to-command 'kubectl apply -f -'
```
2. Ensure the following resources exist in the default namespace.
  - A Deployment called ``.
  - A Pod called ``.
  - A Service Account called ``.
  - A ClusterRole called ``.
  - A ClusterRoleBinding called ``.
3. Ensure the Pod is running.

#### Deploy and Delete a Custom Pod Autoscaler

This tests that a running CPA can be deployed, resources are created, and then
deleted and all resources deleted by the CPAO.

1. Install either the cluster wide or namespace wide operator on a cluster.
2. Deploy a sample CPA, from the `/examples` directory in the Custom Pod
   Autoscaler Base GitHub repository.
   - Deploy using `kubectl apply -f <EXAMPLE_YAML_FILE>`
3. Ensure the following resources are created in the namespace targeted by the
   example YAML file.
   - A Deployment.
   - A Pod.
   - A Service Account.
   - A Role.
   - A RoleBinding.
4. Delete the CPA using `kubectl delete cpa <NAME_OF_CPA>`
5. Ensure all resources listed above are deleted.

## Continuous Integration Pipeline

The CPAB and CPAO utilise *Continous Integration pipelines* (or CI pipelines) -
specifically GitHub Actions. These CI pipelines allow ongoing code quality
checking, testing and building of projects on a commit basis. Every time a new
commit or pull request is submitted to either projects' GitHub repository a
series of checks are executed through GitHub Actions:

- Linting (static code analysis)
- Testing
- Building
- Publishing

This automatic process ensures that any code that is in the main branch of
either project has been linted, tested and can be built without errors. Building
and publishing as part of this CI process allows for reproducible, versioned builds, and
addresses issues of trust for distributables as all artifacts are built on the
CI server rather than on a personal computer.

## Codecov

Code coverage from unit tests is tracked and logged through *Codecov*, a code
coverage tracking tool that allows coverage comparisons and checks between
commits, releases and branches. This tool is useful for ensuring that any code
committed to the main branch is appropriately tested, meeting minimum coverage
criteria. The Codecov tool also provides a badge for displaying test coverage
for a project, which is displayed on each projects' `README.md` files to allow
potential users to have confidence in each project.

\newpage

# Evaluation

## Predictive Horizontal Pod Autoscaler comparision with Horizontal Pod Autoscaler for seasonal loads 

Aiming to validate the utility of the Predictive Horizontal Pod Autoscaler (PHPA)
for autoscaling a K8s cluster with realistic data this experiment was
created to provide a suitable comparison with the existing K8s HPA.

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
K8s autoscaling walkthroughs. The load testing application will be a
python script that will invoke Locust load testing at set intervals, varying the
load applied based on the time of day. The load testing will also periodically
record how many replicas the deployment has. Figure \ref{phpa_long_phpa_diagram}
shows the experiment overview for the PHPA, while figure
\ref{phpa_long_hpa_diagram} shows the experiment overview for the HPA.


This experiment will run for 3 days and is designed to have the PHPA and HPA 
running in their own clusters. 

![Predictive Horizontal Pod Autoscaler Experiment\label{phpa_long_phpa_diagram}](predictive-horizontal-pod-autoscaler/long/diagrams/PHPA_long_experiment_k8s_hpa_design.svg) 

![K8s Horizontal Pod Autoscaler Experiment\label{phpa_long_hpa_diagram}](predictive-horizontal-pod-autoscaler/long/diagrams/PHPA_long_experiment_k8s_hpa_design.svg) 

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
  - Per Interval: `1` (Run every interval)
  - Alpha: `0.1`
  - Beta: `0.1`
  - Gamma: `0.9`
  - Season Length: `5760` (24 hours in 15 second intervals)
  - Stored Seasons: `4` (store last 4 days data)
  - Method: `additive`

### Hypothesis

The Predictive Horizontal Pod Autoscaler using the Holt-Winters prediction
method will pre-emptively scale compared to the standard K8s Horizontal
Pod Autoscaler which will only retroactively react. This will be manifested in
higher replica counts when scaling up, and scaling up earlier; with the result
of lower average and maximum latency, and less failed requests - primarily
around the moment of change from lower load levels to high load. This effect
will only be apparant after at least one full season (24 hours); for the
first season as the predictor won't have data to make a prediction therefore it
is expected to have approximately the same performance as the standard
K8s Horizontal Pod Autoscaler.

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

![Replica comparison\label{phpa_rep_compare}](predictive-horizontal-pod-autoscaler/long/results/replica_compare.svg)

![Average latency comparison\label{phpa_avg_compare}](predictive-horizontal-pod-autoscaler/long/results/avg_latency_compare.svg)

![Average latency comparison for day 1\label{phpa_avg_compare_1}](predictive-horizontal-pod-autoscaler/long/results/avg_latency_day_1.svg)

![Average latency comparison for day 2\label{phpa_avg_compare_2}](predictive-horizontal-pod-autoscaler/long/results/avg_latency_day_2.svg)

![Average latency comparison for day 3\label{phpa_avg_compare_3}](predictive-horizontal-pod-autoscaler/long/results/avg_latency_day_3.svg)

![Maximum latency comparison\label{phpa_max_compare}](predictive-horizontal-pod-autoscaler/long/results/max_latency_compare.svg)

![Maximum latency comparison for day 1\label{phpa_max_compare_1}](predictive-horizontal-pod-autoscaler/long/results/max_latency_day_1.svg)

![Maximum latency comparison for day 2\label{phpa_max_compare_2}](predictive-horizontal-pod-autoscaler/long/results/max_latency_day_2.svg)

![Maximum latency comparison for day 3\label{phpa_max_compare_3}](predictive-horizontal-pod-autoscaler/long/results/max_latency_day_3.svg)

### Conclusion

The PHPA outperforms the HPA in reduction of average latency spikes due to
increased load for seasonal data. The PHPA provides a valuable tool for
proactive autoscaling, and if applied to regular, predictable and repeating user
loads it can provide a more effective autoscaling solution than the standard
K8s HPA. However, the key to effective use of the PHPA is that it needs
to be data driven, and as such requires tuning to be effective and useful. The
PHPA should be applied in specific circumstances in which it makes sense; the
decision to apply it should be driven by an understanding of the system it is
being applied to and it should be backed with data to allow for better tuning
and a more useful autoscaling solution; otherwise unwanted results such as
erratic scaling behaviour may arise out of poor tuning decisions.

The PHPA project is available here:
[https://github.com/jthomperoo/predictive-horizontal-pod-autoscaler](https://github.com/jthomperoo/predictive-horizontal-pod-autoscaler)

## Autoscaling based on Twitter activity

An example of the flexibility of the CPAF is looking at a novel type of
autoscaler that scales based on twitter activity, looking for certain characters
in tweets with a specific hashtag. The autoscaler operates by counting the
number of tweets that contain a thumbs up emoji and the number of tweets that
contain a thumbs down emoji and sets the number of replicas to the difference
between number of tweets containing thumbs up and thumbs down. 

This type of autoscaler would not be possible with the K8s HPA, and would
require a custom autoscaler to be created. This autoscaler exists as an example
of a CPA, and is represented by a small codebase containing two python scripts,
some YAML configuration and a Dockerfile. This level of conciseness would simply
not be possible if implementing an autoscaler from scratch without using the
CPAF.

This example is available here:
[https://github.com/jthomperoo/custom-pod-autoscaler/tree/master/example/scale-on-tweet](https://github.com/jthomperoo/custom-pod-autoscaler/tree/master/example/scale-on-tweet)

## Horizontal Pod Autoscaler running as Custom Pod Autoscaler comparison with Kubernetes HPA

To show that the CPAF does not limit developer control over autoscaling, and to
provide a useful base project for other autoscalers, the HPA was reimplemented
as a CPA. This reimplementation supports all configuration available to the K8s
HPA, while having the additional benefit that this customisation can be done on
a per HPA basis, rather than cluster wide. The K8s HPA configuration requires
SSH access to the master node, making this configuration unavailable on managed
K8s providers such as EKS or GKE - the HPA as a CPA allows configuration at
deploy time without any requirement to SSH into the master node, allowing
configuration on managed providers.

This project is available here:
[https://github.com/jthomperoo/horizontal-pod-autoscaler](https://github.com/jthomperoo/horizontal-pod-autoscaler)

## Game Server Scaling

The Agones Fleet Autoscaler has been identified as a game server specific
autoscalings solution. This autoscaler is a custom implementation by the Agones
development team specific for the Agones framework. The autoscaler allows two
types of autoscaling, webhook based and buffer based. The webhook autoscaling
technique is similar to how the CPAF works, allowing custom user logic to define
how the scaling behaviour works - with the key difference that the CPAF is
generalised and works for all K8s clusters, rather than the Agones Fleet
Autoscaler only working within Agones. The buffer autoscaling technique can be
easily implemented through a CPA and the CPAF, for example with the use of a
Python script. The buffer autoscaling again only works in Agones, but the CPAF
would allow the autoscaler to work in any K8s environment and framework.

## Delivery of Requirements

### Must Have

- [✓] Can deploy a Docker image with autoscaling application into a K8s cluster.
  - [✓] Multiple distributed Docker images for various languages/environments.
    - [✓] Python Docker image.
    - [✓] Alpine Docker image.
- [✓] Autoscaler repeatedly runs.
- [✓] Supports user logic, can triggered through a shell command, allows
  specification in any language/framework that supports being called through
  shell commands.
  - [✓] Supports HTTP requests from user logic.
- [✓] If user logic specifies that the number of replicas should change, scaling
  should occur and the number of pods should be adjusted.
- [✓] \>= 70% Unit test coverage.
- [✓] Can be deployed with K8s YAML.
- [✓] K8s Custom Resource specifiying the Custom Pod Autoscaler to allow for
  simpler and easier deployment/configuration.
- [✓] Syntax validation for Custom Pod Autoscaler K8s YAML.
- [✓] Deploying the K8s Custom Resource should provision all required K8s
  resources for the autoscaler.
- [✓] Can deliver configuration options through K8s YAML.
- [✓] Can deliver configuration options through a supplied configuration file
  baked into the autoscaler image.
- [✓] Configuration options.
  - [✓] How frequently the autoscaler runs.
  - [✓] Minimum and Maximum replicas
  - [✓] Which resource to target for scaling.
  - [✓] Timeouts for metric and evaluation gathering.
- [✓] Can delete the autoscaler.
  - [✓] Deletes all associated K8s resources.

### Should Have

- [✓] *Cooldown* feature to avoid *thrashing*.
- [ ] Allow choosing which pods to terminate when scaling down.
- [✓] Manual triggering of the Custom Pod Autoscaler metric gathering and evaluation
  through an API.
  - [✓] Provide a *dry run* flag to the API to allow seeing how the autoscaler would
    scale without applying the results.
- [✓] Hooks for different actions/stages in the autoscaling process.
    - [✓] Before metric gathering.
    - [✓] After metric gathering.
    - [✓] Before evaluation.
    - [✓] After evaluation.
    - [✓] Before scaling.
    - [✓] After scaling.
- [✓] Support scaling all resources the Horizontal Pod Autoscaler can scale.
  - [✓] ReplicaSets.
  - [✓] ReplicationControllers.
  - [✓] StatefulSets.
  - [✓] Deployments.
- [ ] Methods for calling user logic.
  - [ ] Can trigger user logic through an HTTP request, allowing logic to exist
    outside of the autoscaling pod, or even outside of the cluster.
- [✓] Metric gathering modes.
  - [✓] Can run in a *per pod* autoscaling mode, which will run metric gathering
    for each pod the targeted resource manages.
  - [✓] Can run in a *per resource* autoscaling mode, which will run metric
    gathering only once for the targeted resource.
- [✓] Full customisation of K8s resources, allowing Custom Pod Autoscalers to define
  their own resource dependencies.
  - [✓] When this customised resource is provided, the Custom Pod Autoscaler
    should have ownership; meaning if the autoscaler is deleted the resource is
    deleted.
- [ ] Custom Pod Autoscaler GUI.
- [✓] Implemented Custom Pod Autoscalers.
  - [✓] Horizontal Pod Autoscaler; reimplemented as a Custom Pod Autoscaler.
  - [✓] Predictive Horizontal Pod Autoscaler; Horizontal Pod Autoscaler extended
    with statistical prediction techniques.
  - [✓] Load Testing Pod Autoscaler; autoscaler allowing scaling based on realtime
    load tested data.
  - [✓] Examples to help developers.
    - [✓] Autoscaler written in Python.
    - [✓] Autoscaler written in Golang.
    - [✓] Autoscaler that scales based on Twitter activity.

### Undelivered Requirements

- Allow choosing which pods to terminate when scaling down.

This requirement was not met, as the K8s scaling API does not support this.
Implementations that did not use the K8s scaling API were brittle and prone to
version changes. There is currently an open issue for this feature on the K8s
GitHub repository [@k8s_specific_downscale].

- Can trigger user logic through an HTTP request, allowing logic to exist
  outside of the autoscaling pod, or even outside of the cluster.  

This requirement was not met at time of submission due to time constraints, but
there are plans for a future release to support this.

- Custom Pod Autoscaler GUI.

This requirement was not met as it was decided that this would not be a useful
tool, it's use would be very limited and any usecase would be covered easily by
the CPAB HTTP REST API.

### Delivered Requirements

The vast majority of requirements were met, with the CPAF meeting all of the
*must have* requirements set out in the requirements section - while meeting
most of the *should have* requirements. 

\newpage

# Conclusion

The CPAF is a useful framework and tooling set, allowing easy and fast
development of custom autoscalers for Kubernetes. The CPAF directly addresses
the problems identified, allowing full customisation of autoscaler logic in a
less complex fashion. The CPAF is completely flexible, supporting a wide
variety of languages, environment and frameworks. The entire HPA can be
reimplemented as a CPA using the CPAF, displaying that there is no reduction in
control or customisation when using the CPAF. The open source nature of the CPAF
allows it to mature as a toolset, with the possiblity of third party developers
and users using and maintaining the CPAF - giving some guarantee to the
longevity of the project. This project has achieved the aims and goals it was
created for, addressing the problems with a novel approach that gives complete
control to developers and cluster administrators.

\newpage
