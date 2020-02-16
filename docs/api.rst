.. _ref-api:

API Documentation
=================
Remember: One of the motive behind the existence of stockroom is the simplicity and
that's what we have considered whenever we added or removed a new API. What does that
mean? It means that we have tried hard to keep the number of APIs to a minimum
while catering the requirements of a developer. Here we discuss the python APIs
available in stockroom.

Initialization
--------------
.. automodule:: stockroom.init_repo()
    :members:

StockRoom class
---------------
.. autoclass:: stockroom.StockRoom()
   :members:

Storages
--------
Stockroom introduces three different storages for different storage needs and all the
APIs in stockroom is to deal with these storages


.. autoclass:: stockroom.storages.Data()
   :members:

.. autoclass:: stockroom.storages.Model()
   :members:

.. autoclass:: stockroom.storages.Tag()
   :members:
