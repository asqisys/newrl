lsof -P | grep 8090 | awk '{print $2}' | xargs kill -9
