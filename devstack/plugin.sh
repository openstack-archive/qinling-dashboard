# plugin.sh - DevStack plugin.sh dispatch script qinling-dashboard

QINLING_DASHBOARD_DIR=$(cd $(dirname $BASH_SOURCE)/.. && pwd)

function install_qinling_dashboard {
    # NOTE(shu-mutou): workaround for devstack bug: 1540328
    # where devstack install 'test-requirements' but should not do it
    # for qinling-dashboard project as it installs Horizon from url.
    # Remove following two 'mv' commands when mentioned bug is fixed.
    mv $QINLING_DASHBOARD_DIR/test-requirements.txt $QINLING_DASHBOARD_DIR/_test-requirements.txt

    setup_develop ${QINLING_DASHBOARD_DIR}

    mv $QINLING_DASHBOARD_DIR/_test-requirements.txt $QINLING_DASHBOARD_DIR/test-requirements.txt
}

function configure_qinling_dashboard {
    cp -a ${QINLING_DASHBOARD_DIR}/qinling_dashboard/enabled/* ${DEST}/horizon/openstack_dashboard/local/enabled/
    cp -a ${QINLING_DASHBOARD_DIR}/qinling_dashboard/conf/qinling_policy.json ${DEST}/horizon/openstack_dashboard/conf/
    # NOTE: If locale directory does not exist, compilemessages will fail,
    # so check for an existence of locale directory is required.
    if [ -d ${QINLING_DASHBOARD_DIR}/qinling_dashboard/locale ]; then
        (cd ${QINLING_DASHBOARD_DIR}/qinling_dashboard; DJANGO_SETTINGS_MODULE=openstack_dashboard.settings $PYTHON ../manage.py compilemessages)
    fi
}

# check for service enabled
if is_service_enabled qinling-dashboard; then

    if [[ "$1" == "stack" && "$2" == "pre-install"  ]]; then
        # Set up system services
        # no-op
        :

    elif [[ "$1" == "stack" && "$2" == "install"  ]]; then
        # Perform installation of service source
        echo_summary "Installing Qinling Dashboard"
        install_qinling_dashboard

    elif [[ "$1" == "stack" && "$2" == "post-config"  ]]; then
        # Configure after the other layer 1 and 2 services have been configured
        echo_summary "Configuring Qinling Dashboard"
        configure_qinling_dashboard

    elif [[ "$1" == "stack" && "$2" == "extra"  ]]; then
        # no-op
        :
    fi

    if [[ "$1" == "unstack"  ]]; then
        # no-op
        :
    fi

    if [[ "$1" == "clean"  ]]; then
        # Remove state and transient data
        # Remember clean.sh first calls unstack.sh
        # no-op
        :
    fi
fi
