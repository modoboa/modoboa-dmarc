modoboa-dmarc
=============

|gha| |codecov|

A set of tools to use DMARC through Modoboa.

This plugin is still in BETA stage, for now it only parses XML aggregated
reports and generate visual reports (using c3.js) on a per-domain basis.

Installation
------------
Make sure to install the following additional system package according to your distribution:

+-----------------+
| Debian / Ubuntu |
+=================+
| libmagic1       |
+-----------------+

+------------+
| CentOS     |
+============+
| file-devel |
+------------+

Install this extension system-wide or inside a virtual environment by
running the following command::

  $ pip install modoboa-dmarc

Edit the settings.py file of your modoboa instance and add
``modoboa_dmarc`` inside the ``MODOBOA_APPS`` variable like this::

    MODOBOA_APPS = (
      'modoboa',
      'modoboa.core',
      'modoboa.lib',
      'modoboa.admin',
      'modoboa.limits',
      'modoboa.relaydomains',
      'modoboa.parameters',
      # Extensions here
      'modoboa_dmarc',
    )

Run the following commands to setup the database tables::

  $ cd <modoboa_instance_dir>
  $ python manage.py migrate modoboa_dmarc
  $ python manage.py collectstatic
  $ python manage.py load_initial_data
    
Finally, restart the python process running modoboa (uwsgi, gunicorn,
apache, whatever).

Integration with Postfix
------------------------

A management command is provided to automatically parse DMARC
aggregated reports (rua) and feed the database. The execution of this
command can be automated with the definition of a postfix service and
a custom transport table.

First, declare a new service in ``/etc/postfix/master.cf``::

  dmarc-rua-parser unix  -       n       n       -       -       pipe
    flags= user=vmail:vmail argv=<path to python> <path to modoboa instance>/manage.py import_aggregated_report --pipe

Define a new transport table inside ``/etc/postfix/main.cf``::

  transport_maps =
      hash:/etc/postfix/dmarc_transport
      # other transport maps...

Create a file called ``/etc/postfix/dmarc_transport`` with the following content::

  <email address your declared in your DNS record>  dmarc-rua-parser:

Hash the file using the following command::

  $ postmap /etc/postfix/dmarc_transport

Finally, reload postfix::

  $ service postfix reload


Specific Upgrade Instructions
-----------------------------

1.3.0
~~~~~

modoboa-dmarc now requires an additional system package according to your distribution:

+-----------------+
| Debian / Ubuntu |
+=================+
| libmagic1       |
+-----------------+

+------------+
| CentOS     |
+============+
| file-devel |
+------------+


.. |gha| image:: https://github.com/modoboa/modoboa-dmarc/actions/workflows/plugin.yml/badge.svg
   :target: https://github.com/modoboa/modoboa-dmarc/actions/workflows/plugin.yml

.. |codecov| image:: https://codecov.io/gh/modoboa/modoboa-dmarc/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/modoboa/modoboa-dmarc
