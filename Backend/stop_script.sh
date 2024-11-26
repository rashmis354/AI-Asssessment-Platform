port=8585
pid=$(lsof -t -i :$port)

if [ -z "$pid" ]; then  
    echo "No process found running on port $port."
else  
    echo "Process with PID $pid is running on port $port. Killing it..."  
    kill -9 $pid  
    echo "Process killed." 
fi 