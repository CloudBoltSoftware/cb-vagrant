#!/bin/bash

# Set default router -- we want to route everything through the host system
# to ensure that applicable packets are routed over the host's VPN.
# NOTE: this means that a VPN to the CB network is required, even if the local
# network, e.g. office network, is bridged to the CB network.
route add default gw 10.0.2.2

# Delete default gw on eth1 which we're assuming is the bridged network.
eval `route -n | awk '{ if ($8 =="eth1" && $2 != "0.0.0.0") print "route del default gw " $2; }'`
