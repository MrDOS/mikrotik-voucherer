#! /usr/bin/env python3

import argparse
import sys

from . import credentials, mikrotik

def main():
    parser = argparse.ArgumentParser(
        'mikrotik-voucherer',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '-U',
        '--username-template',
        default=credentials.DEFAULT_USERNAME_TEMPLATE,
        help='a regular expression describing the desired username format',
    )
    parser.add_argument(
        '-P',
        '--password-template',
        default=credentials.DEFAULT_PASSWORD_TEMPLATE,
        help='a regular expression describing the desired password format',
    )
    parser.add_argument(
        '-d',
        '--duration',
        default=4 * 60 * 60,
        help='lifetime of the generated user (in seconds)',
    )
    parser.add_argument(
        '-a',
        '--address',
        type=str,
        help='the IP address of the MikroTik device',
    )
    parser.add_argument(
        '-i',
        '--identity',
        type=str,
        help='the identity of the MikroTik device',
    )
    parser.add_argument(
        '-u',
        '--username',
        type=str,
        required=True,
        help='the administrative username for the MikroTik device',
    )
    parser.add_argument(
        '-p',
        '--password',
        type=str,
        required=True,
        help='the administrative password for the MikroTik device',
    )
    args = parser.parse_args()

    if args.address is None and args.identity is None:
        parser.error('Either the IP address or identity of the MikroTik device must be provided!')

    if args.address is None and args.identity is not None:
        args.address = mikrotik.find(args.identity)

        if args.address is None:
            parser.error('Could not find a MikroTik device with that identity!')

    device = mikrotik.RouterOSDevice(args.address)
    device.login(args.username, args.password)

    print(credentials.generate(args.username_template, args.password_template))

if __name__ == '__main__':
    sys.exit(main())
