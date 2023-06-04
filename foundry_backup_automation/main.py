import argparse
import os
from datetime import date
from logging import INFO, basicConfig, error, info

import paramiko
from dotenv import load_dotenv


def connect_to_server(key_path, server_ip, port, username):
    """
    Establishes an SSH connection to the remote server using the provided credentials.

    Args:
        key_path (str): Path to the private key file.
        server_ip (str): Remote server server_ip or IP address.
        port (int): SSH port number.
        username (str): SSH username.

    Returns:
        paramiko.SSHClient: Established SSH session.
    """
    try:
        session = paramiko.SSHClient()
        session.load_system_host_keys()
        session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        private_key = paramiko.RSAKey.from_private_key_file(key_path)
        session.connect(server_ip, port, username, pkey=private_key)
    except paramiko.AuthenticationException:
        error('Authentication failed. Please check the SSH credentials.')
        return
    except Exception as e:
        error(f'An error occurred during connection: {e}')
        return
    
    info(f'Connection established on {username}@{server_ip}.')
    return session


def zip_folder(session, remote_directory, remote_zip_filename):
    """
    Zips a remote folder on the server.

    Args:
        session (paramiko.SSHClient): Established SSH session.
        remote_directory (str): Path to the remote directory to be zipped.
        remote_zip_filename (str): Name of the remote ZIP file to be created.
    """
    zip_command = f'zip -r {remote_zip_filename} {remote_directory}'
    _, stdout, _ = session.exec_command(zip_command)
    stdout.read()
    info('Folder zipped.')


def download_zip_folder(
    session,
    remote_zip_filename,
    save_download_directory,
    local_zip_filename,
):
    """
    Downloads a ZIP file from the remote server.

    Args:
        session (paramiko.SSHClient): Established SSH session.
        remote_zip_filename (str): Name of the remote ZIP file to be downloaded.
        save_download_directory (str): Local directory to save the downloaded ZIP file.
        local_zip_filename (str): Name of the ZIP file to be saved locally.
    """
    sftp = session.open_sftp()
    save_download_local_path = os.path.join(
        save_download_directory, local_zip_filename
    )
    sftp.get(remote_zip_filename, save_download_local_path)
    sftp.close()
    info('ZIP file downloaded.')


def delete_zip_and_close(session, remote_zip_filename):
    """
    Deletes the remote ZIP file and closes the SSH session.

    Args:
        session (paramiko.SSHClient): Established SSH session.
        remote_zip_filename (str): Name of the remote ZIP file to be deleted.
    """
    session.exec_command(f'rm {remote_zip_filename}')
    session.close()
    info('ZIP file deleted from server.')


def main(args):
    load_dotenv(dotenv_path=args.args_file)
    hoje = date.today()
    
    basicConfig(
        level=INFO,
        filename=os.getenv('LOG_FILE_PATH', 'foundry_backup_automation.log'),
        filemode='a',
        encoding='utf-8',
        format='%(asctime)s - %(levelname)s - %(message)s',
    )

    try:
        key_path = os.environ['KEY_PATH']
        server_ip = os.environ['SERVER_IP']
        port = int(os.environ['PORT'])
        username = os.environ['REMOTE_USERNAME']
        remote_directory = os.environ['REMOTE_DIRECTORY']
        remote_zip_filename = os.environ['REMOTE_ZIP_FILE_NAME']
        remote_zip_filename = (
            f'{remote_zip_filename}_{hoje.strftime("%d_%m_%Y")}.zip'
        )
        save_download_directory = os.environ['SAVE_DOWNLOAD_DIRECTORY']
        local_zip_filename = os.environ['LOCAL_ZIP_FILE_NAME']
        local_zip_filename = (
            f'{local_zip_filename}_{hoje.strftime("%d_%m_%Y")}.zip'
        )
    except KeyError as e:
        error(f'Environment variable {e} not found!')
        return
    except ValueError as e:
        error(f'Environment variable PORT must be an integer!')
        return
    except Exception as e:
        error(f'Unexpected error: {e}')
        return

    session = connect_to_server(key_path, server_ip, port, username)
    try:
        zip_folder(session, remote_directory, remote_zip_filename)
        download_zip_folder(
            session,
            remote_zip_filename,
            save_download_directory,
            local_zip_filename,
        )
        print(f'Backup {remote_zip_filename} was successfully downloaded!')
    finally:
        delete_zip_and_close(session, remote_zip_filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Backup Foundry CLI')
    parser.add_argument('args_file', help='Path to the configuration file')
    args = parser.parse_args()

    main(args)
