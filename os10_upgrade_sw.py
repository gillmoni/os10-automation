import logging
import paramiko
import time

# Set the variables for the switch IP, username, and password
switch_ip = '100.104.49.86'
username = 'admin'
password = 'admin'

# Set the variables for the firmware file path and name
firmware_base = 'build-eqx-01.force10networks.com/neteng/netarchive1/devbuild/archive/' 
firmware_filename = 'Enterprise-installer-x86_64.bin'
firmware_suffix = 'AmazonInstallers/'

firmware_release = 'FMB-ar-rel_10.5.4-release/'
firmware_integration = 'FMB-integration-release/'
firmware_build = 'latest-build-201/'

firmware_file_path = firmware_base + firmware_release + firmware_suffix + firmware_build

# http://build-eqx-01.force10networks.com/neteng/netarchive1/devbuild/archive/FMB-ar-rel_10.5.4-release/AmazonInstallers/last_good/

# Change the levels in this line
logging.basicConfig(
    level=logging.INFO,
    filename="upgrade.log",
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filemode='a'  # Specify the file mode (write)
)

logging.info(f'Image path [{firmware_file_path}]')

# Connect to the switch using SSH
ssh_client = paramiko.SSHClient()

# Automatically add the switch's host key
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Connect to switch
ssh_client.connect(switch_ip, username=username, password=password, timeout=30)
logging.info(f'Sucessfully connected to switch {switch_ip}')

# Send the command to upload the firmware file to the switch
http_command = f'image install http://{firmware_file_path}{firmware_filename}'
logging.info(f'Sending command [{http_command}]')
stdin, stdout, stderr = ssh_client.exec_command(http_command)
output = stdout.read().decode('utf-8')
error = stderr.read().decode('utf-8')
logging.info(f'Command sent!')

cmd = "show image status | grep Progress"
stdin, stdout, stderr = ssh_client.exec_command(cmd)
output = stdout.read().decode('utf-8')
error = stderr.read().decode('utf-8')
logging.info(f'Output {output}')

sleep_time, interval = 300, 30
while sleep_time > 0:
    cmd = "show image status | grep Progress"
    stdin, stdout, stderr = ssh_client.exec_command(cmd)
    output = stdout.read().decode('utf-8')
    logging.info(f'Time left [{sleep_time - interval}] {output}')
    time.sleep(interval)
    sleep_time -= interval

if error:
    logging.critical(f"Error uploading firmware file: {error}")
else:
    logging.info(f"Uploaded firmware file: {firmware_filename}")

# Close the SSH connection
ssh_client.close()

def upgrade_image():
    # Send the command to upgrade the switch firmware
    upgrade_command = f'image install image:\/\/{firmware_filename}'
    logging.debug(f"Upgrade CMD [{upgrade_command}]")
    stdin, stdout, stderr = ssh_client.exec_command(upgrade_command)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    if error:
        logging.fail(f"Error upgrading firmware: {error}")
        return True
    else:
        logging.info("Firmware upgrade successful")
        return False
