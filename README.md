# Command line interface for NodeODM

### Usage:

```
nodeodmcli [-h] [-s SERVER] [-p PORT] [-t TOKEN] [-o OUTDIR] [--name TASKNAME] [--timeout TIMEOUT] [--options OPTIONS] [--version] folder
```
```
positional arguments:
  folder                Photo folder

options:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
                        Hostname or IP address of processing node
  -p PORT, --port PORT  Port of processing node
  -t TOKEN, --token TOKEN
                        Token to use for authentication
  -o OUTDIR, --output OUTDIR
                        Absolute path to save output files (defaults to photo folder)
  --name TASKNAME       User-friendly name for the task
  --timeout TIMEOUT     Timeout value in seconds for network requests
  --options OPTIONS     Task' settings (preset filename or json string)
  --version             show program's version number and exit

Copyright 2024, Sandro Klippel
```