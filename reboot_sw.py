from datetime import datetime
import logging
import time
import paramiko

# Change the levels in this line
logging.basicConfig(
    level=logging.DEBUG,
    filename="monitor.log",
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Set the IP address, username, and password of the switch
host = "100.104.49.40"
username = "admin"
password = "admin"

# Create an SSH client object
client = paramiko.SSHClient()

reboot_times = 1
while True:
	logging.info(f'Reboot Try {reboot_times}')
	# Automatically add the switch's host key
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	# Connect to the switch
	client.connect(hostname=host, username=username, password=password, timeout=None)

	# Schedule the switch to reboot after a delay of 5 minutes
	command = "dir show"
	stdin, stdout, stderr = client.exec_command(command)
	output = stdout.read().decode()
	logging.info(output)

	# Open an interactive shell session on the remote server
	shell = client.invoke_shell()

	# Wait for the shell prompt to appear
	while not shell.recv_ready():
	    pass

	# Send the "reboot" command to the remote server
	shell.send("reload\n")

	# Wait for the confirmation prompt to appear
	while not shell.recv_ready():
	    pass

	# Send the "no" response to the confirmation prompt
	shell.send("yes\n")

	# Wait for the server to reboot and print the output
	time.sleep(10)  # Wait for the server to reboot (adjust as necessary)
	while shell.recv_ready():
	    output = shell.recv(1024)
	    logging.info(output.decode("utf-8"))

	if b'confirm yes' in output:
		logging.info("Reboot prompt detected")
	else:
		continue

	logging.info(output)
	logging.info("Command Finished")
	logging.info(f'Reboot[{reboot_times}] completed')
	logging.info("Now waiting till next reboot")

	reboot_times += 1
	# Wait for 5 minutes
	time.sleep(240)

# Disconnect from the switch
client.close()

