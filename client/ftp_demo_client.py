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

        # Enter command loop
        synth_prompt = False
        while (1):
            # Recieve and print command prompt, send user response
            if synth_prompt == False:
                prompt = await receive_long_message(reader)
            else:
                synth_prompt = False
                print("Enter Command: ")
            command = input(prompt)
            # Command Handlers
            # List command
            if command == "list":
                await send_long_message(writer, command)
                response = await receive_long_message(reader)
                print (response)
                continue
            # Put command
            elif len(command) > 2 and command[:3] == "put":
                #Check that file exists
                filename = command[4:]
                if not os.path.isfile("./" + filename):
                    print ("NAK Invalid File Name")
                    synth_prompt = True
                    continue
                # If file exists, send put followed by filename and contents of file
                await send_long_message(writer, "put " + filename)
                with open(filename, 'r') as f:
                    await send_long_message(writer, f.read())
                # Recieve and print ACK
                print(await receive_long_message(reader))
            # Get Command
            elif len(command) > 2 and command[:3] == "get":
                # Send get command to server
                await send_long_message(writer, command)
                # Receive and print response
                response = await receive_long_message(reader)
                if (response[:3] == "NAK"):
                    #If NAK, print and we're done
                    print(response)
                    continue
                # Otherwise, download file and print ACK
                filename = command[4:]
                with open(filename, "x") as f:
                    # Get file contents and write them to new file
                    f.write(response[4:])
                print("ACK")
            # Remove Command
            elif len(command) > 5 and command[:6] == "remove":
                # Send command to server
                await send_long_message(writer, command)
                # Receive response and print
                response = await receive_long_message(reader)
                print (response)
            # Close Command
            elif len(command) > 4 and command[:5] == "close":
                # Send command to server, receive ACK, and end loop
                await send_long_message(writer, command)
                print (await receive_long_message(reader))
                break

        return

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

# Run the `main()` function
if __name__ == "__main__":
    
    asyncio.run(main())
