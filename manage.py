#!/usr/bin/env python
import sys
from server import execute_from_command_line

if __name__ == '__main__':
    execute_from_command_line(['server.py'] + sys.argv[1:])
