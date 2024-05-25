#! /usr/bin/env python3

import argparse
import sys

from . import client, server

def main():
    parser = argparse.ArgumentParser('mikrotik-voucherer')
    subparsers = parser.add_subparsers(required=True)

    server.register(subparsers)
    client.register(subparsers)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    sys.exit(main())
