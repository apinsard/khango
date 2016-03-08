Khango
======

This project is very experimental. Don't use it.

The goal of khango is to abstract views and templates creation at the highest
level, even though it means less scalability.

You can see it as alternative to `django.contrib.admin` with extended
features and more scalability.


Core features
-------------

- Select only requested fields
- Guess `select_related` and `prefetch_related` according to the fields list
- Provide various content types for the same URI according to "Accept" header:
  - text/html
  - application/json
  - application/xml
  - ...
- Built-in responsive templates for each generic view
