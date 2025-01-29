import socket
import struct


def main():
    print("DNS Server is running on 127.0.0.1:2053...")
    
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # UDP socket is created and bound to the local address 127.0.0.1 on port 2053
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("127.0.0.1", 2053))
    
    class DNSHeader:
        def __init__(self, ID=0, flag=0, QDCOUNT=0, ANCOUNT=0, NSCOUNT=0, ARCOUNT=0):
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
 
    while True:
        try:
            # Receive a DNS query
            buf, source = udp_socket.recvfrom(512)
            header = DNSHeader(ID=1234, QDCOUNT=1)
            header = header.pack()
            print(f"Received request from {source}")

            response = b""
            response = b"\x04\xd2\x80" + (b"\x00" * 9)
    
            udp_socket.sendto(response, source)
        except Exception as e:
            print(f"Error receiving data: {e}")
            break


if __name__ == "__main__":
    main()
