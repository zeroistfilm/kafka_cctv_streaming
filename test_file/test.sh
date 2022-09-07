#!/bin/bash

sudo nc -U /var/run/netifyd/netifyd.sock | jq . -C
