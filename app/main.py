import socket
import struct

class DNSHeader:
        def __init__(self, QDCOUNT, ID=1234, flags=0x8000, ANCOUNT=1, NSCOUNT=0, ARCOUNT=0):
            self.ID = ID
            self.flags = flags # 0x8000 sets QR bit to 1 (response)
            self.QDCOUNT = QDCOUNT
            self.ANCOUNT = ANCOUNT
            self.NSCOUNT = NSCOUNT
            self.ARCOUNT = ARCOUNT
    
        def pack(self):
            return struct.pack("!HHHHHH",
            self.ID,
            self.flags,
            self.QDCOUNT,
            self.ANCOUNT,
            self.NSCOUNT,
            self.ARCOUNT)    
 
class DNSQuestion:
    """
    Initialize a DNS question.
    :param qname: The domain name being queried (e.g., "example.com").
    :param qtype: The type of query (e.g., 1 for A record).
    :param qclass: The class of query (e.g., 1 for IN - Internet).
    """
    def __init__(self, qname, qtype=1, qclass=1):
        self.qname = qname
        self.qtype = qtype
        self.qclass= qclass

    def pack(self):
        labels = self.qname.split(".")
        packed_name = b''.join([bytes([len(label)]) + label.encode('utf-8') for label in labels]) + b'\x00'
        return packed_name + struct.pack('!HH', self.qtype, self.qclass)

#ResourceRecord        
class DNSAnswer:
    def __init__(self, rname, rtype=1, rclass=1, ttl=60, rdlength=4, rdata=socket.inet_aton("8.8.8.8")):
        self.rname = rname
        self.rtype = rtype
        self.rclass = rclass
        self.ttl = ttl #time-to-live
        self.rdlength = rdlength
        self.rdata = rdata

    def pack(self):
        labels = self.rname.split(".")
        packed_name = b''.join([bytes([len(label)]) + label.encode('utf-8') for label in labels]) + b'\x00'
        packed_fixed = struct.pack('!HHIH', self.rtype, self.rclass, self.ttl, self.rdlength)
        return packed_name + packed_fixed + self.rdata

def main():
    print("DNS Server is running on 127.0.0.1:2053...")
    
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # UDP socket is created and bound to the local address 127.0.0.1 on port 2053
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("127.0.0.1", 2053))
    
    while True:
        try:
            # Receive a DNS query
            buf, source = udp_socket.recvfrom(512)

            question = DNSQuestion(qname="codecrafters.io").pack()
            print(f"Receiving question from {question}")

            # Create an answer (example: responding with an A record)
            answer = DNSAnswer(rname="codecrafter.io").pack()

            header = DNSHeader(QDCOUNT=1).pack()
            print(f"Received request from {source}")

            response = header + question + answer
            #response = b"\x04\xd2\x80" + (b"\x00" * 9)
    
            udp_socket.sendto(response, source)
        except Exception as e:
            print(f"Error receiving data: {e}")
            break


if __name__ == "__main__":
    main()