=================================
Use Qinling Dashboard in DevStack
=================================

Set up your ``local.conf`` to enable qinling-dashboard::

    [[local|localrc]]
    enable_plugin qinling-dashboard https://git.openstack.org/openstack/qinling-dashboard


.. note::

    You also need to install Qinling itself into DevStack to use Qinling Dashboard.
