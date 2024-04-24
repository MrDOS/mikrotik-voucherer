#! /usr/bin/env python3

import sys

# If we're running from within a wheel (`python voucherer`) instead of as a
# module (`python -m voucherer`), we need to make sure the parent directory of
# the wheel is on the path so we can import the wheel.
if __package__ == '':
    import os.path
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, path)

import voucherer

if __name__ == '__main__':
    sys.exit(voucherer.main())
