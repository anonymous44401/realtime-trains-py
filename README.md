# Realtime Trains API Python Module

---

Maintained and managed by anonymous44401

![PyPI](https://img.shields.io/pypi/v/realtime-trains-py) ![License](https://img.shields.io/github/license/anonymous44401/realtime-trains-py) ![Issues](https://img.shields.io/github/issues/anonymous44401/realtime-trains-py) ![Downloads](https://img.shields.io/pypi/dm/realtime-trains-py)

### Quick links
[Latest release](https://github.com/anonymous44401/realtime-trains-py/releases/latest)

[Pre-releases](https://test.pypi.org/project/realtime-trains-py/)

[Documentation](https://github.com/anonymous44401/realtime-trains-py/wiki/Home)

[Repository](https://github.com/anonymous44401/realtime-trains-py)

## About this package

**realtime-trains-py** is an open-source python API Wrapper designed to allow you to access data directly from the Realtime Trains API, in a simple and user-friendly way. This package includes three different [complexity modes](https://github.com/anonymous44401/realtime-trains-py/wiki/Complexity) that allow you to customise how you want to see the data provided by the API.

This package can be used for anything railway related. Whether you're a rail enthusiast or commuter, this package can be used for all your purposes. The package can be used in **personal** applications or for **personal** rail data access. For **commercial** use, you should contact [Realtime Trains](https://www.realtimetrains.co.uk/). More information can be found on their [API home page](https://api-portal.rtt.io/welcome/)

This package is not affiliated with [Realtime Trains](https://www.realtimetrains.co.uk/). 

## What can I do with this package?
This package allows you to access data directly from the [Realtime Trains API](https://api-portal.rtt.io/welcome/) using one of [three complexities](https://github.com/anonymous44401/realtime-trains-py/wiki/Complexity). Each complexity mode gives you access to different data the API offers. 

For the most flexibility, you can use **simple** mode, the recommended mode. Simple mode allows you to access a fair amount of the data available from the Realtime Trains API. This mode is recommended for those that want a manageable amount of information while keeping it easy to read. Use `complexity="simple"`.

Using simple mode, you can optionally select between prettier or normal mode. The default, prettier mode, gives you your data in a nicely formatted table, while normal mode gives you your data as objects, so you'll need to get the data out of the objects yourself. To use normal mode, use `complexity="simple_normal"`. Don't worry though! If you're confused, we have plenty of [documentation](https://github.com/anonymous44401/realtime-trains-py/wiki/Home) to help you out.

For the most freedom with the API, you can use **complex** mode. Complex mode lets you access all the data available from the Realtime Trains API. This mode does not format any data for you - it creates new `.json` files with the data you requested. This mode is recommended for those who have a good understanding of python and managing json files. Use `complexity="complex"`.

## Installation Instructions

To install the package, simply run the following command in your terminal:
```
$ pip install realtime-trains-py
``` 
Alternatively, you can clone, fork or download the [repository](https://github.com/anonymous44401/realtime-trains-py) onto your device. 

Once installed, you can import the package. Place the lines below in your file or you can run them directly in your terminal.
```python
from realtime_trains_py import RealtimeTrainsPy

rtt = RealtimeTrainsPy(
    request_token="<your_request_token>", 
    complexity="<your_choice>"
)
```

Check out our full [setup guide](https://github.com/anonymous44401/realtime-trains-py/wiki/Setup) for more help setting up.

You'll need an account for the [Realtime Trains API](https://api-portal.rtt.io/welcome/) to use this package. You can sign up for free at the [API home page](https://api-portal.rtt.io/welcome/). 


## Examples

#### Get Live
###### The example below will display a live departure board for Ely. 
```python
rtt.get_live(tiploc="ELYY")
```

#### Get Departures
###### The example below will return up to 15 rows on the departure board for London King's Cross at the time you run the program. 
```python
rtt.get_departures(tiploc="KNGX", rows=15)
```

#### Get Service
###### The example below will return the service information of G28171 at the time you run the program. 
```python
rtt.get_service(service_uid="G28171")
```

More in-depth examples can be found on our [examples page](https://github.com/anonymous44401/realtime-trains-py/wiki/Examples). 


## Licensing 

The **realtime-trains-py** API Wrapper uses an MIT License.

All data is kindly provided by [Realtime Trains](https://www.realtimetrains.co.uk/) through the [Realtime Trains API](https://api-portal.rtt.io/welcome/). This package is not affiliated with [Realtime Trains](https://www.realtimetrains.co.uk/).
