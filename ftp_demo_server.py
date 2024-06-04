# Owen LeMaster, 933669069
# Willem van Veldhuisen, 934499197
import socket
import asyncio
import os
os.chdir('server/myfiles')

INTERFACE, SPORT = 'localhost', 8080
CHUNK = 100


intro_message = "ACK Hello! Welcome to my vanveldw, owen's server! I'm majoring in CS\n"

# TODO: Implement me for Part 1!
async def send_intro_message(writer, reader, message):
    # Strings for messages
    password = "password"
    pass_prompt = "Please enter password: "
    invalid_pass = "\nNAK Invalid Password\n"
    valid_pass = False
    # Prompt for password
    for i in range(1, 4):
        await send_long_message(writer, pass_prompt)
        response = await receive_long_message(reader)
        if response == password:
            valid_pass = True
            break
        else:
            await send_long_message(writer, invalid_pass)
    # If user guessed password, send intro message
    if valid_pass == True:
        await send_long_message(writer, intro_message)
        return True
    # Otherwise, return false to indicate failure
    return False


def to_hex(number):
    # Verify our assumption: error is printed and program exists if assumption is violated
    assert number <= 0xffffffff, "Number too large"
    return "{:08x}".format(number)


async def send_long_message(writer: asyncio.StreamWriter, data):
    # TODO: Send the length of the message: this should be 8 total hexadecimal digits
    #       This means that ffffffff hex -> 4294967295 dec
    #       is the maximum message length that we can send with this method!
    #       hint: you may use the helper function `to_hex`. Don't forget to encode before sending!

    writer.write(to_hex(len(data)).encode())
    writer.write(data.encode())

    await writer.drain()


# TODO: Implement me for Part 2!
async def receive_long_message(reader: asyncio.StreamReader):
    # First we receive the length of the message: this should be 8 total hexadecimal digits!
    # Note: `socket.MSG_WAITALL` is just to make sure the data is received in this case.
    data_length_hex = await reader.readexactly(8)

    # Then we convert it from hex to integer format that we can work with
    data_length = int(data_length_hex, 16)

    full_data = await reader.readexactly(data_length)
    return full_data.decode()


async def handle_client(reader, writer):
    """
    Part 1: Introduction
    """
    # If password is invalid, end handle_client
    if await send_intro_message(writer, reader, intro_message) == False:
        writer.close()
        await writer.wait_closed()
        return
    return
    """
    Part 2: FTP Protocol
    """

    # Receive the filename from the client
    filename = await receive_long_message(reader)

    # Send an acknowledgement
    await send_intro_message(writer, "ACK")

    # TODO: Implement function above
    message = await receive_long_message(reader)

    # Write the contents of the long message into a file
    with open("./server_data/" + filename, 'w') as f:
        f.write(message)

    print("Wrote to file ./server_data/" + filename)

    writer.close()
    await writer.wait_closed()


async def main():
    server = await asyncio.start_server(
            handle_client,
            INTERFACE, SPORT
    )

    async with server:
        await server.serve_forever()

# Run the `main()` function
if __name__ == "__main__":
    asyncio.run(main())
