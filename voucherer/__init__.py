#! /usr/bin/env python3

import argparse
import sys

from . import credentials

def main():
    parser = argparse.ArgumentParser(
        'mikrotik-voucherer',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '-u',
        '--username-template',
        default=credentials.DEFAULT_USERNAME_TEMPLATE,
        help='a regular expression describing the desired username format',
    )
    parser.add_argument(
        '-p',
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
    args = parser.parse_args()

    print(credentials.generate(args.username_template, args.password_template))

if __name__ == '__main__':
    sys.exit(main())
