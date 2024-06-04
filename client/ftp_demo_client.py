# Owen LeMaster, 933669069
# Willem van Veldhuisen, 934499197
import socket
from time import sleep
from threading import Thread
import asyncio
import os
os.chdir('myfiles')

IP, DPORT = 'localhost', 8080

# Helper function that converts integer into 8 hexadecimal digits
# Assumption: integer fits in 8 hexadecimal digits
def to_hex(number):
    # Verify our assumption: error is printed and program exists if assumption is violated
    assert number <= 0xffffffff, "Number too large"
    return "{:08x}".format(number)

# Function for checking password and getting intro message
async def recv_intro_message(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    # Prompt user with server password prompt
    for i in range(1, 4):
        pass_prompt = await receive_long_message(reader)
        pass_attempt = input(pass_prompt)
        await send_long_message(writer, pass_attempt)
        #Receive NAK or intro
        response = await receive_long_message(reader)
        if "NAK" not in response:
            return response
        print (response)
    return None



# TODO: Implement me for Part 1!
async def recv_message(reader: asyncio.StreamReader):
    full_data = await reader.readline()
    return full_data.decode()
    

# TODO: Implement me for Part 2!
async def send_long_message(writer: asyncio.StreamWriter, data):
    # TODO: Send the length of the message: this should be 8 total hexadecimal digits
    #       This means that ffffffff hex -> 4294967295 dec
    #       is the maximum message length that we can send with this method!
    #       hint: you may use the helper function `to_hex`. Don't forget to encode before sending!

    writer.write(to_hex(len(data)).encode())
    writer.write(data.encode())

    await writer.drain()


async def receive_long_message(reader: asyncio.StreamReader):
    # First we receive the length of the message: this should be 8 total hexadecimal digits!
    # Note: `socket.MSG_WAITALL` is just to make sure the data is received in this case.
    data_length_hex = await reader.readexactly(8)

    # Then we convert it from hex to integer format that we can work with
    data_length = int(data_length_hex, 16)

    full_data = await reader.readexactly(data_length)
    return full_data.decode()


async def connect():
    # Configure a socket object to use IPv4 and TCP
    reader, writer = await asyncio.open_connection(IP, DPORT)

    """
    Part 1: Introduction
    """

    try:
        # TODO: receive the introduction message by implementing `recv_intro_message` above.
        intro = await recv_intro_message(reader, writer)
        if intro == None:
            print ("Too many attempts, closing connection")
            return
        print(intro)
        return

        # Get the filename to send from the user
        filename = ""
        while True:
            filename = input("Enter filename to send: ")
            if os.path.isfile("./client_data/" + filename):
                break
            print("Invalid filename.")

        # Send the filename to the server
        await send_long_message(writer, filename)

        # Receive a response from the server
        await recv_message(reader)


        # Read in the contents of the file
        with open("./client_data/" + filename, 'r') as f:
            tosend = f.read()

        # Send the file contents to the server
        long_msg = f"{tosend}"

        """
        Part 2: Long Message Exchange Protocol
        """
        # TODO: Send message to the server by implementing `send_long_message` above.
        await send_long_message(writer, long_msg)

    finally:
        writer.close()
        await writer.wait_closed()



    return 0

async def main():
    tasks = []
    for i in range(1):
        tasks.append(connect())
    #await connect(str(0).rjust(8, '0'))

    await asyncio.gather(*tasks)
    print("done")

# Run the `main()` function
if __name__ == "__main__":
    
    asyncio.run(main())
