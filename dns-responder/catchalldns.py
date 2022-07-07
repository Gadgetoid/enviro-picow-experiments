"""
MIT license
(C) Konstantin Belyalov 2018
"""
import uasyncio as asyncio
import usocket as socket
import logging
import gc


DNS_QUERY_START = const(12)
log = logging.getLogger('DNS')


class DNSQuery:
    def __init__(self, data):
        self.data = data
        self.domain = ""
        # header is bytes 0-11, so question starts on byte 12
        head = 12
        # length of this label defined in first byte
        length = data[head]
        while length != 0:
            label = head + 1
            # add the label to the requested domain and insert a dot after
            self.domain += data[label : label + length].decode("utf-8") + "."
            # check if there is another label after this one
            head += length + 1
            length = data[head]

    def answer(self, ip_addr):
        # ** create the answer header **
        # copy the ID from incoming request
        packet = self.data[:2]
        # set response flags (assume RD=1 from request)
        packet += b"\x81\x80"
        # copy over QDCOUNT and set ANCOUNT equal
        packet += self.data[4:6] + self.data[4:6]
        # set NSCOUNT and ARCOUNT to 0
        packet += b"\x00\x00\x00\x00"

        # ** create the answer body **
        # respond with original domain name question
        packet += self.data[12:]
        # pointer back to domain name (at byte 12)
        packet += b"\xC0\x0C"
        # set TYPE and CLASS (A record and IN class)
        packet += b"\x00\x01\x00\x01"
        # set TTL to 60sec
        packet += b"\x00\x00\x00\x3C"
        # set response length to 4 bytes (to hold one IPv4 address)
        packet += b"\x00\x04"
        
        # now actually send the IP address as 4 bytes (without the "."s)
        packet += bytes(map(int, ip_addr.split(".")))

        gc.collect()

        return packet


class CatchallDNS():
    """Tiny DNS server aimed to serve very small deployments like "captive portal"
    """

    def __init__(self, address="0.0.0.0", ttl=10, max_pkt_len=256):
        self.ttl = ttl
        self.max_pkt_len = max_pkt_len
        self.sock = None
        self.task = None
        self.addr = address

    async def __handler(self):
        while True:
            try:
                yield asyncio.core._io_queue.queue_read(self.sock)
                packet, addr = self.sock.recvfrom(self.max_pkt_len)
                
                q = DNSQuery(packet)
                
                self.sock.sendto(q.answer(self.addr), addr)

            except asyncio.CancelledError:
                # Coroutine has been canceled
                self.sock.close()
                self.sock = None
                return
            except AttributeError:
                raise
            except Exception as e:
                log.exc(e, "")

    def run(self, host='127.0.0.1', port=53):
        # Start UDP server
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        addr = socket.getaddrinfo(host, port, 0, socket.SOCK_DGRAM)[0][-1]
        sock.setblocking(False)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(addr)
        self.sock = sock
        self.task = self.__handler()
        asyncio.get_event_loop().create_task(self.task)

    def shutdown(self):
        if self.task:
            asyncio.cancel(self.task)
            self.task = None
