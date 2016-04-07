#!/bin/bash

if [ "$1" == 'router' ]
  then
    exec python3 python-router/all_routes.py

elif [ "$1" == 'service' ]
  then
    exec python3 python-service/all_routes.py

else
    python3 python-service/all_routes.py &
    exec python3 python-router/all_routes.py

fi