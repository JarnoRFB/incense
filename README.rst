.. image:: https://travis-ci.org/JarnoRFB/incense.svg?branch=master
    :target: https://travis-ci.org/JarnoRFB/incense

Incense
=======

Though automated logging of machine learning experiments results is
crucial, it does not replace manual interpretation. Incense is a toolbox
to facilitate manual interpretation of experiments that are logged using
`sacred <https://github.com/IDSIA/sacred>`__. It lets you find and
evaluate experiments directly in Jupyter notebooks. Incense lets you
query the database for experiments by id, name or any hyperparmeter
value. For each found experiment, configuration, artifacts and metrics
can be displayed. The artifacts are rendered according to their type,
e.g. a PNG image is displayed as an image, while a CSV file gets
transformed to a ``pandas DataFrame``. Metrics are by default
transformed into ``pandas Series``, which allows for flexible plotting.
Together with sacred and incense, Jupyter notebooks offer the perfect
solution for interpreting experiments as they allow for a combination of
code that reproducibly displays the experiment’s results, as well as
text that contains the interpretation.

Installation
------------
To use incense you need the newest development version of sacred, so that
content-types of artifacts are automatically detected. Therefore, you first
have to install sacred from github and then install incense from PyPI.

::

   pip install git+https://github.com/IDSIA/sacred.git
   pip install incense

Documentation
-------------

`demo.ipynb <demo.ipynb>`_ demonstrates the basic functionality of
incense.
