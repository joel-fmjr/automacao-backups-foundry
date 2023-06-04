# Foundry Backup Automation

This script automates the backup process for the Foundry application by performing the following steps:

1. Connects to a remote server via SSH using the provided credentials.
2. Zips a specified remote directory on the server.
3. Downloads the generated ZIP file to a local directory.
4. Deletes the remote ZIP file.

## Prerequisites

- Python 3.10 or higher

## Configuration

1. Create a virtual environment (optional but recommended):
   ```shell
   python -m venv venv
   source venv/bin/activate
   ```
2. install the required dependencies
    ```shell
   pip install -r requirements.txt
   ```

3. Create a configuration file (`config.env`) following the `args_file_template.env` in this repo.

## Usage
To manually run the script, use the following commands:

1. Activate the virtual environment (if you created one):
    ```shell
    source venv/bin/activate
    ```
    
2. Run the script
    ```shell
    python main.py /path/to/config.env
    ```

## Scheduling with Cron
To schedule the script using cron or any other task scheduler, you can follow these steps:

1. Open the cron table for editing:
    ```shell
    crontab -e
    ```

2. Add an entry to the cron table to run the script at the desired schedule. For example, to run the script daily at 08:00 AM, you can add the following line:
    ```shell
    00 08 * * * . /path/to/venv/bin/activate && python /path/to/repo/foundry_backup_automation/main.py /path/to/config.env>
    ```
    Make sure to adjust the paths to the Python interpreter, main script, configuration file, and log file based on your setup.
