import socket
import struct

#DNSHeader
class DNSHeader:
        def __init__(self, ID, OPCODE, RD, QR=1, AA=0, TC=0, RA=0, Z=0, RCODE=0, QDCOUNT=1, ANCOUNT=1, NSCOUNT=0, ARCOUNT=0):
            self.ID = ID
            self.OPCODE = OPCODE
            self.RD = RD
            self.QR = QR # 0x8000 sets QR bit to 1 (response)
            self.AA = AA
            self.TC = TC
            self.RA = RA
            self.Z = Z
            self.RCODE = RCODE
            #self.flags = flags # 0x8000 sets QR bit to 1 (response)
            self.QDCOUNT = QDCOUNT
            self.ANCOUNT = ANCOUNT
            self.NSCOUNT = NSCOUNT
            self.ARCOUNT = ARCOUNT
    
        # Pack the header into a byte string.
        def pack(self):
            flags = (self.QR << 15) | (self.OPCODE << 11) | (self.AA << 10) | (self.TC << 9) | (self.RD << 8) | (self.RA << 7) | (self.Z << 4) | self.RCODE
            return struct.pack("!HHHHHH",
            self.ID,
            flags,
            self.QDCOUNT,
            self.ANCOUNT,
            self.NSCOUNT,
            self.ARCOUNT)    
        
        # Unpack a header from a byte string.
        @classmethod
        def unpack(cls, data):
            ID, flags, QDCOUNT, ANCOUNT, NSCOUNT, ARCOUNT = struct.unpack("!HHHHHH", data)
            QR = (flags >> 15) & 0x1
            OPCODE = (flags >> 11) & 0xF
            AA = (flags >> 10) & 0x1
            TC = (flags >> 9) & 0x1
            RD = (flags >> 8) & 0x1
            RA = (flags >> 7) & 0x1
            Z = (flags >> 4) & 0x7
            RCODE = flags & 0xF
            return cls(ID, OPCODE, RD, QR, AA, TC, RA, Z, RCODE, QDCOUNT, ANCOUNT, NSCOUNT, ARCOUNT)

#DNSQuestion
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

    # Pack the question into a byte string.
    def pack(self):
        labels = self.qname.split(".")
        packed_name = b''.join([bytes([len(label)]) + label.encode('utf-8') for label in labels]) + b'\x00'
        return packed_name + struct.pack('!HH', self.qtype, self.qclass)

    # Unpack a question from a byte string.
    @classmethod
    def unpack(cls, data, offset=0):
        qname = []
        while True:
            length = data[0]
            if length == 0:
                offset += 1
                break
            # Check if the length is a pointer
            if length & 0xC0 == 0xC0:
                pointer = struct.unpack('!H', data[offset:offset+2])[0] & 0x3FFF
                qname.append(cls.unpack(data[pointer:])[0])
                offset += 2
                break
            else:
                offset += 1

            qname.append(data[offset:offset+length].decode('utf-8'))
            offset += length
            
        qtype, qclass = struct.unpack('!HH', data[offset:offset+4])
        return cls(".".join(qname), qtype, qclass), offset + 4

#ResourceRecord        
class DNSAnswer:
    def __init__(self, rname, rtype=1, rclass=1, ttl=60, rdlength=4, rdata=socket.inet_aton("8.8.8.8")):
        self.rname = rname
        self.rtype = rtype
        self.rclass = rclass
        self.ttl = ttl #time-to-live
        self.rdlength = rdlength
        self.rdata = rdata #The function socket.inet_aton("8.8.8.8") converts the IPv4 address "8.8.8.8" from its dotted-quad string format to a 32-bit packed binary format
    
    # Pack the resource record into a byte string.
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
            print(f"Received {len(buf)} of {buf} bytes from {source}")

            # Unpack the header
            query_header = DNSHeader.unpack(buf[:12])
            
            RCODE = 0 if query_header.OPCODE == 0 else 4

            header = DNSHeader(ID=query_header.ID, RD=query_header.RD, OPCODE=query_header.OPCODE, RCODE=RCODE).pack()
            print(f"Received request from {source}")

            # Unpack the question
            query_question = DNSQuestion.unpack(buf[12:])

            question = DNSQuestion(qname=query_question.qname).pack()
            print(f"Receiving question from {question}")

            # Create an answer (example: responding with an A record)
            answer = DNSAnswer(rname=query_question.qname).pack()
            print(f"Anwser: {answer}")

            response = header + question + answer
            #response = b"\x04\xd2\x80" + (b"\x00" * 9)
    
            udp_socket.sendto(response, source)
        except Exception as e:
            print(f"Error receiving data: {e}")
            break


if __name__ == "__main__":
    main()