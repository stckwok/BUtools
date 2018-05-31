# Copyright (C) 2018 nCrypt / Bitcoin Unlimited developers
#
# This file is part of BU Tools.
#
# It is subject to the license terms in the LICENSE file found in the top-level
# directory of this distribution.

#!/usr/bin/env python2

def validip(ip):
    """Test if ip address is valid
    inputs
        IP address to validate
    return 
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