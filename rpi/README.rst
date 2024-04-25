Raspberry Pi configuration files
================================

This is an incomplete set of configuration files
used on the Raspberry Pi Zero 2 W that I run this project on.

``bootfs/custom.toml`` is (something like)
the unattended installation configuration
that I used on first boot.
Obviously, my SSH key has been removed because it's useless to you,
and my Wi-Fi credentials have been removed to protect the guilty.

``rootfs/etc/gpio/22`` is the `systemd-gpio`_ configuration
that I use to trigger the voucherer on a button push.

.. _systemd-gpio: https://github.com/nasa-gcn/systemd-gpio
