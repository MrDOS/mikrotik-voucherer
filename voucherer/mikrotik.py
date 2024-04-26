#! /usr/bin/env python3

import binascii
import hashlib
import posix
import socket
import ssl
import sys

DISCOVERY_PORT = 5678
DISCOVERY_TIMEOUT = 5
DISCOVERY_REQUEST = b'\x00\x00\x00\x00'

API_PORT = 8728
API_PORT_SECURE = 8729

class RouterOSDevice(object):
    """
    RouterOS API client.

    Based on https://help.mikrotik.com/docs/display/ROS/Python3+Example.
    """
    sock: socket.socket

    def __init__(self, address: str, port: [int, None]=None, secure=True):
        if port is None:
            port = API_PORT_SECURE if secure else API_PORT

        info = socket.getaddrinfo(address, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
        af, socktype, proto, canonname, sockaddr = info[0]
        self.sock = socket.socket(af, socktype, proto)

        if secure:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            ctx.set_ciphers('ADH-AES128-SHA256:@SECLEVEL=0')
            self.sock = ctx.wrap_socket(self.sock)

        self.sock.connect(sockaddr)

    def login(self, username, password):
        for reply, attrs in self.talk([
                "/login",
                f"=name={username}",
                f"=password={password}",
            ]):
            if reply == '!trap':
                return False
            elif '=ret' in attrs.keys():
                challenge = binascii.unhexlify((attrs['=ret']).encode(sys.stdout.encoding))
                hash = hashlib.md5()
                hash.update(b'\x00')
                hash.update(password.encode(sys.stdout.encoding))
                hash.update(challenge)
                for reply2, attrs2 in self.talk([
                        "/login",
                        f"=name={username}",
                        f"=response=00{binascii.hexlify(hash.digest()).decode(sys.stdout.encoding)}",
                    ]):
                    if reply2 == '!trap':
                        return False
        return True

    def talk(self, words):
        if self.writeSentence(words) == 0: return
        r = []
        while 1:
            i = self.readSentence();
            if len(i) == 0: continue
            reply = i[0]
            attrs = {}
            for w in i[1:]:
                j = w.find('=', 1)
                if (j == -1):
                    attrs[w] = ''
                else:
                    attrs[w[:j]] = w[j+1:]
            r.append((reply, attrs))
            if reply == '!done': return r

    def writeSentence(self, words):
        ret = 0
        for w in words:
            self.writeWord(w)
            ret += 1
        self.writeWord('')
        return ret

    def readSentence(self):
        r = []
        while 1:
            w = self.readWord()
            if w == '': return r
            r.append(w)

    def writeWord(self, w):
        print(("<<< " + w))
        self.writeLen(len(w))
        self.writeStr(w)

    def readWord(self):
        ret = self.readStr(self.readLen())
        print((">>> " + ret))
        return ret

    def writeLen(self, l):
        if l < 0x80:
            self.writeByte((l).to_bytes(1, sys.byteorder))
        elif l < 0x4000:
            l |= 0x8000
            tmp = (l >> 8) & 0xFF
            self.writeByte(((l >> 8) & 0xFF).to_bytes(1, sys.byteorder))
            self.writeByte((l & 0xFF).to_bytes(1, sys.byteorder))
        elif l < 0x200000:
            l |= 0xC00000
            self.writeByte(((l >> 16) & 0xFF).to_bytes(1, sys.byteorder))
            self.writeByte(((l >> 8) & 0xFF).to_bytes(1, sys.byteorder))
            self.writeByte((l & 0xFF).to_bytes(1, sys.byteorder))
        elif l < 0x10000000:
            l |= 0xE0000000
            self.writeByte(((l >> 24) & 0xFF).to_bytes(1, sys.byteorder))
            self.writeByte(((l >> 16) & 0xFF).to_bytes(1, sys.byteorder))
            self.writeByte(((l >> 8) & 0xFF).to_bytes(1, sys.byteorder))
            self.writeByte((l & 0xFF).to_bytes(1, sys.byteorder))
        else:
            self.writeByte((0xF0).to_bytes(1, sys.byteorder))
            self.writeByte(((l >> 24) & 0xFF).to_bytes(1, sys.byteorder))
            self.writeByte(((l >> 16) & 0xFF).to_bytes(1, sys.byteorder))
            self.writeByte(((l >> 8) & 0xFF).to_bytes(1, sys.byteorder))
            self.writeByte((l & 0xFF).to_bytes(1, sys.byteorder))

    def readLen(self):
        c = ord(self.readStr(1))
        # print (">rl> %i" % c)
        if (c & 0x80) == 0x00:
            pass
        elif (c & 0xC0) == 0x80:
            c &= ~0xC0
            c <<= 8
            c += ord(self.readStr(1))
        elif (c & 0xE0) == 0xC0:
            c &= ~0xE0
            c <<= 8
            c += ord(self.readStr(1))
            c <<= 8
            c += ord(self.readStr(1))
        elif (c & 0xF0) == 0xE0:
            c &= ~0xF0
            c <<= 8
            c += ord(self.readStr(1))
            c <<= 8
            c += ord(self.readStr(1))
            c <<= 8
            c += ord(self.readStr(1))
        elif (c & 0xF8) == 0xF0:
            c = ord(self.readStr(1))
            c <<= 8
            c += ord(self.readStr(1))
            c <<= 8
            c += ord(self.readStr(1))
            c <<= 8
            c += ord(self.readStr(1))
        return c

    def writeStr(self, str):
        n = 0;
        while n < len(str):
            r = self.sock.send(bytes(str[n:], 'UTF-8'))
            if r == 0: raise RuntimeError("connection closed by remote end")
            n += r

    def writeByte(self, str):
        n = 0;
        while n < len(str):
            r = self.sock.send(str[n:])
            if r == 0: raise RuntimeError("connection closed by remote end")
            n += r

    def readStr(self, length):
        ret = ''
        # print ("length: %i" % length)
        while len(ret) < length:
            s = self.sock.recv(length - len(ret))
            if s == b'': raise RuntimeError("connection closed by remote end")
            # print (b">>>" + s)
            # atgriezt kaa byte ja nav ascii chars
            if s >= (128).to_bytes(1, "big") :
               return s
            # print((">>> " + s.decode(sys.stdout.encoding, 'ignore')))
            ret += s.decode(sys.stdout.encoding, "replace")
        return ret

def find(identity: str):
    """Find the IP address of a device from its LLDP-advertised identity."""

    identity = bytes(identity, 'UTF-8')

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind(('<broadcast>', DISCOVERY_PORT))

        sock.sendto(DISCOVERY_REQUEST, ('<broadcast>', DISCOVERY_PORT))

        sock.settimeout(DISCOVERY_TIMEOUT)
        while True:
            try:
                data, addr = sock.recvfrom(1024)

                if data == DISCOVERY_REQUEST:
                    continue

                # HACK(SC): I don't really care to parse the discovery packets
                # right now. Just doing a substring match is really dirty, but
                # also doesn't sound super likely to return false positives.
                if identity in data:
                    return addr[0]
            except socket.timeout:
                return None
