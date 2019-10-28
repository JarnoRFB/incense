.. image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/JarnoRFB/incense/master?urlpath=lab/tree/demo.ipynb

.. image:: https://travis-ci.org/JarnoRFB/incense.svg?branch=master
    :target: https://travis-ci.org/JarnoRFB/incense

.. image:: https://codecov.io/gh/JarnoRFB/incense/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/JarnoRFB/incense

.. image:: https://img.shields.io/lgtm/grade/python/g/JarnoRFB/incense.svg?logo=lgtm&logoWidth=18
    :target: https://lgtm.com/projects/g/JarnoRFB/incense/context:python

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black

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

::

   pip install incense

Documentation
-------------

`demo.ipynb <demo.ipynb>`_ demonstrates the basic functionality of
incense. You can also try it out interactively on
`binder <https://mybinder.org/v2/gh/JarnoRFB/incense/master?urlpath=lab/tree/demo.ipynb>`_.

Contributing
------------
We recommend using the `VSCode devcontainer <https://code.visualstudio.com/docs/remote/containers>`_ for development.
It will automatically install all dependencies and start
necessary services, such as mongoDB and JupyterLab.
See `<.devcontainer/docker-compose.yml>`_ for details.
Building the container for the first time may take some time.
Once in the container run

::

  $ pre-commit install
  $ python tests/example_experiment/conduct.py


to set up the pre-commit hooks and populate the example database.

Alternatively, you can use conda to set up your local development environment.

::

  $ conda create -n incense-dev python=3.6
  $ conda activate incense-dev
  # virtualenv is required for the precommit environments.
  $ conda install virtualenv
  # tox-conda is required for using tox with conda.
  $ pip install tox-conda
  $ pip install -r requirements-dev.txt
  $ pre-commit install
