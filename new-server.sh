#!/bin/bash

# call when some new server is added to github
git pull
pm2 restart all
