lsof -P | grep 8092 | awk '{print $2}' | xargs kill -9
lsof -P | grep 8091 | awk '{print $2}' | xargs kill -9
