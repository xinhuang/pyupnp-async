************
pyupnp-async
************

A Python library for UPnP operations using asyncio.

Currently this library only provided convenience for port forwarding using UPnP. For other UPnP features, it is
possible, but manual construction of request parameters is needed. (I.E. the SOUP request XML.)

Installation
============

To install the latest development version, run:

::

  git clone https://github.com/xinhuang/pyupnp-async.git
  cd pyupnp-async
  python setup.py install

*This package is not on pypi.*

Quick Tutorial
==============

Create a port forwarding using UPnP:

.. code:: python

  from pyupnp_async import msearch_first
  
  async def forward_port(local_ip, local_port, ext_port, protocol):
      resp = await msearch_first('urn:schemas-upnp-org:device:InternetGatewayDevice:1')
      device = await resp.get_device()
      service = device.find_first_service('urn:schemas-upnp-org:service:WANIPConnection:1')
      ext_ip = await service.get_external_ip_address()
      try:
          await service.add_port_mapping(local_port, ext_port, local_ip, protocol)
          print('Data to external Port {} will be forwarded to {}:{}'.format(ext_port, local_ip, local_port))
      except UpnpSoapError as e:
          print(e)

Delete a port forwarding using UPnP:

.. code:: python

  from pyupnp_async import msearch_first
  
  async def stop_forwarding(ext_port, protocol):
      resp = await msearch_first('urn:schemas-upnp-org:device:InternetGatewayDevice:1')
      device = await resp.get_device()
      service = device.find_first_service('urn:schemas-upnp-org:service:WANIPConnection:1')
      ext_ip = await service.get_external_ip_address()
      try:
          await service.delete_port_mapping(ext_port, protocol)
          print('Data to external Port {} will not be forwarded any more.')
      except UpnpSoapError as e:
          print(e)

API Reference
=============

``msearch_first(search_target='upnp:rootdevice', max_wait=2, loop=None)``

Searches for UPnP target specified, and returns the first responsed target.

  :Args:
    * ``search_target``: Search target. For details please reference to UPnP spec.
    * ``max_wait``: Specify max waiting time in seconds.
    * ``loop``: Specify the event loop to be used. Default is ``asyncio.get_event_loop()``

``msearch_first(search_target='upnp:rootdevice', max_wait=2, loop=None)``

Searches for UPnP target specified, and returns all targets responded in given time range as an async iterator.

  :Args:
    * ``search_target``: Search target. For details please reference to UPnP spec.
    * ``max_wait``: Specify max waiting time in seconds.
    * ``loop``: Specify the event loop to be used. Default is ``asyncio.get_event_loop()``

Licensing
=========

This project is released under the terms of the MIT Open Source License. View
*LICENSE.txt* for more information.

