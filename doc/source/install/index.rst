====================================
Qinling Dashboard installation guide
====================================

This page describes the manual installation of qinling-dashboard,
while distribution packages may provide more automated process.

.. note::

   This page assumes horizon has been installed.
   Horizon setup is beyond the scope of this page.

Install Qinling Dashboard with all relevant packages to your Horizon environment.

.. code-block:: console

    pip install qinling-dashboard

In most cases, qinling-dashboard is installed into your python "site-packages"
directory like ``/usr/local/lib/python2.7/site-packages``.
We refer to the directory of qinling-dashboard as ``<qinling-dashboard-dir>`` below
and it would be ``<site-packages>/qinling_dashboard`` if installed via pip.
The path varies depending on Linux distribution you use.

To enable qinling-dashboard plugin, you need to put horizon plugin setup files
into horizon "enabled" directory.

The plugin setup files are found in ``<qinling-dashboard-dir>/enabled``.

.. code-block:: console

   $ cp <qinling-dashboard-dir>/enabled/_[1-9]*.py \
         /usr/share/openstack-dashboard/openstack_dashboard/local/enabled

.. note::

   The directory ``local/enabled`` may be different depending on your
   environment or distribution used. The path above is one used in Ubuntu
   horizon package.

Configure the policy file for qinling-dashboard in OpenStack Dashboard
``local_settings.py``.

.. code-block:: python

   POLICY_FILES['function_engine'] = '<qinling-dashboard-dir>/conf/qinling_policy.json'

.. note::

   If your ``local_settings.py``  has no ``POLICY_FILES`` yet,
   you need to define the default ``POLICY_FILES`` in
   ``local_settings.py``. If you use the example ``local_settings.py`` file
   from horizon, what you need is to uncomment ``POLICY_FILES`` (which contains
   the default values).

Compile the translation message catalogs of qinling-dashboard.

.. code-block:: console

   $ cd <qinling-dashboard-dir>
   $ python ./manage.py compilemessages

Run the Django update commands.
Note that ``compress`` is required when you enable compression.

.. code-block:: console

   $ cd <horizon-dir>
   $ DJANGO_SETTINGS_MODULE=openstack_dashboard.settings python manage.py collectstatic --noinput
   $ DJANGO_SETTINGS_MODULE=openstack_dashboard.settings python manage.py compress --force

Finally, restart your web server. For example, in case of apache:

.. code-block:: console

   $ sudo service apache2 restart
