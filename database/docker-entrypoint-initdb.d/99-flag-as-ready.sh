#!/bin/bash

# This script creates a flag to tell that the container is ready to be used
# It should be exectued in last

touch /var/lib/postgresql/data/ready.flag
