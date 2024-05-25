#! /usr/bin/env python3

import argparse
import json
import socket
import sys

COMMAND_BUFFER_SIZE = 1024
COMMAND_GENERATE = 'generate'

from . import credentials, mikrotik

def main():
    parser = argparse.ArgumentParser('mikrotik-voucherer')
    subparsers = parser.add_subparsers(required=True)

    serve_parser = subparsers.add_parser(
        'serve',
        help='start a local voucherer server',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    serve_parser.set_defaults(parser=serve_parser, func=serve)
    serve_parser.add_argument(
        '-l',
        '--listen',
        default=7786,
        help='the local port to listen on',
    )
    serve_parser.add_argument(
        '-U',
        '--username-template',
        default=credentials.DEFAULT_USERNAME_TEMPLATE,
        help='a regular expression describing the desired username format',
    )
    serve_parser.add_argument(
        '-P',
        '--password-template',
        default=credentials.DEFAULT_PASSWORD_TEMPLATE,
        help='a regular expression describing the desired password format',
    )
    serve_parser.add_argument(
        '-d',
        '--duration',
        default=4 * 60 * 60,
        help='lifetime of the generated user (in seconds)',
    )
    serve_parser.add_argument(
        '-a',
        '--address',
        type=str,
        help='the IP address of the MikroTik device',
    )
    serve_parser.add_argument(
        '-i',
        '--identity',
        type=str,
        help='the identity of the MikroTik device',
    )
    serve_parser.add_argument(
        '-u',
        '--username',
        type=str,
        required=True,
        help='the administrative username for the MikroTik device',
    )
    serve_parser.add_argument(
        '-p',
        '--password',
        type=str,
        required=True,
        help='the administrative password for the MikroTik device',
    )

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

    args = parser.parse_args()
    args.func(args)

def serve(args):
    if args.address is None and args.identity is None:
        args.parser.error('Either the IP address or identity of the MikroTik device must be provided!')

    if args.address is None and args.identity is not None:
        args.address = mikrotik.find(args.identity)

        if args.address is None:
            args.parser.error('Could not find a MikroTik device with that identity!')

    device = mikrotik.RouterOSDevice(args.address)
    device.login(args.username, args.password)

    # TODO: Catch socket disconnection and attempt reconnection. This should be
    # done in another thread, synchronized by a threading.Event.

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    for addr in socket.getaddrinfo(None, args.listen, server.family, server.type):
        server.bind(addr[-1])

    server.listen()

    while True:
        try:
            conn, address = server.accept()
        except KeyboardInterrupt:
            return

        with conn:
            while True:
                buffer = conn.recv(COMMAND_BUFFER_SIZE)
                if len(buffer) == 0:
                    # Connection dropped.
                    break

                command = buffer.decode().strip()

                if command == COMMAND_GENERATE:
                    creds = credentials.generate(args.username_template, args.password_template)
                    conn.send(json.dumps(creds.__dict__).encode())

def generate(args):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(socket.getaddrinfo(None, args.port, client.family, client.type)[0][-1])

    client.send(COMMAND_GENERATE.encode())
    buffer = client.recv(COMMAND_BUFFER_SIZE)

    print(buffer.decode())

if __name__ == '__main__':
    sys.exit(main())
