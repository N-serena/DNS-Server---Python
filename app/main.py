import socket
import struct

class DNSHeader:
        def __init__(self, QDCOUNT, ID=1234, flag=0, ANCOUNT=0, NSCOUNT=0, ARCOUNT=0):
            self.ID = ID
            self.flag = flag
            self.QDCOUNT = QDCOUNT
            self.ANCOUNT = ANCOUNT
            self.NSCOUNT = NSCOUNT
            self.ARCOUNT = ARCOUNT
    
        def pack(self):
            return struct.pack("!HHHHHH",
            self.ID,
            self.flag,
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
            header = DNSHeader(QDCOUNT=1)
            header = header.pack()
            print(f"Received request from {source}")

            question = DNSQuestion(qname="codecrafter.io", qtype=1, qclass=1)
            question = question.pack()
            print(f"Receiving question from {question}")

            response = header + question
            response = b"\x04\xd2\x80" + (b"\x00" * 9)
    
            udp_socket.sendto(response, source)
        except Exception as e:
            print(f"Error receiving data: {e}")
            break


if __name__ == "__main__":
    main()
