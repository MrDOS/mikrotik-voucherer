#! /usr/bin/env python3

import argparse
import socket

from . import commands

def register(subparsers):
    generate_parser = subparsers.add_parser(
        'generate',
        help='connect to a local voucherer server and generate a set of credentials',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    generate_parser.set_defaults(parser=generate_parser, func=generate)
    generate_parser.add_argument(
        '-p',
        '--port',
        default=7786,
        help='the local port to connect to',
    )

def generate(args):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(socket.getaddrinfo(None, args.port, client.family, client.type)[0][-1])

    client.send(commands.COMMAND_GENERATE.encode())
    buffer = client.recv(commands.COMMAND_BUFFER_SIZE)

    print(buffer.decode())
