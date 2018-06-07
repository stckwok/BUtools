# Copyright (C) 2018 nCrypt / Bitcoin Unlimited developers
#
# This file is part of BU Tools.
#
# It is subject to the license terms in the LICENSE file found in the top-level
# directory of this distribution.

#!/usr/bin/env python2

import time
import subprocess

def validip(ip):
    """Test if ip address is valid
    inputs
        IP address to validate
    returns
        True if valid (False otherwise)
    """
    if ip.count('.') == 3 and all(0<=int(num)<256 for num in ip.rstrip().split('.')): 
      return True
    else:
      raise ValueError('IP address is invalid !')

def isLocalHost(params):
    """Test if localhost is in the parameter list
    inputs
        user input parameters in list
    return 
        True if localhost is in list 
        False otherwise
    """
    if "localhost" in params:
        return True
    else:
        return False

def timeit(method):
    """Decorator to measure the execution time of the method/function
    inputs
        method name
    returns
        execution time in msec
    """
    def timed(*args, **kw):
        tstart = time.time()
        result = method(*args, **kw)
        tend = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((tend - tstart) * 1000)
        else:
            print '%r  %2.2f ms' % \
                  (method.__name__, (tend - tstart) * 1000)
        return result
    return timed

def find_params(hostaddr, param_list):
    """ Find IP address and port from a list of input arguments
    inputs
        hostaddr - string to match for ipaddress
        param_list - list of strings of input arguments
    returns
        host ip adddrsss and RPC listening port
    """
    print("param List = ", param_list)
    for s in filter (lambda x: hostaddr in x, param_list):
        host = s.split(":")

    port = host[1]
    ip = host[0].split("=")[1]
    return ip, port

def hostRunning(ip):
    """Test if host is up and running using ping command
    inputs
        IP address to validate
    returns
        True if host is running (False otherwise)
    """
    try:
      print(">>>> ping -c 1 " + ip)
      output = subprocess.check_output("ping -c 1 " + ip, shell=True)
      #print(output)
    except Exception, e:
      print(e)
      return False

    return True