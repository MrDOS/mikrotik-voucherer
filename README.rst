MikroTik Voucherer
==================

This tool runs as either a daemon
which generates MikroTik `Hotspot user`_ credentials,
and deletes them later once they've expired;
or as a client for that daemon
which prints the credentials
(physically, to a piece of paper).

This tool manages simple Hotspot users
rather than `User Manager`_ users
because I want to use it with a device
which doesn't have enough flash storage capacity
for both the Wi-Fi and User Manager packages.
Alternatively, I could provide generated users to the hotspot via RADIUS;
but seeing as I don't hate myself,
I'm going to not do that instead.

.. _Hotspot user: https://wiki.mikrotik.com/wiki/Manual:IP/Hotspot/User
.. _User Manager: https://help.mikrotik.com/docs/display/ROS/User+Manager
