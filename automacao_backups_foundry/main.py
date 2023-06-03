import argparse
import os

import paramiko
from dotenv import load_dotenv


def connect_to_server(key_path, hostname, port, username):
    """
    Establishes an SSH connection to the remote server using the provided credentials.

    Args:
        key_path (str): Path to the private key file.
        hostname (str): Remote server hostname or IP address.
        port (int): SSH port number.
        username (str): SSH username.

    Returns:
        paramiko.SSHClient: Established SSH session.
    """
    session = paramiko.SSHClient()
    session.load_system_host_keys()
    session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    private_key = paramiko.RSAKey.from_private_key_file(key_path)
    session.connect(hostname, port, username, pkey=private_key)
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


def delete_zip_and_close(session, remote_zip_filename):
    """
    Deletes the remote ZIP file and closes the SSH session.

    Args:
        session (paramiko.SSHClient): Established SSH session.
        remote_zip_filename (str): Name of the remote ZIP file to be deleted.
    """
    session.exec_command(f'rm {remote_zip_filename}')
    session.close()


def main(args):
    load_dotenv(dotenv_path=args.config_file)

    key_path = os.getenv('KEY_PATH')
    hostname = os.getenv('HOSTNAME')
    port = int(os.getenv('PORT'))
    username = os.getenv('REMOTE_USERNAME')
    remote_directory = os.getenv('REMOTE_DIRECTORY')
    remote_zip_filename = os.getenv('REMOTE_ZIP_FILE_NAME')
    save_download_directory = os.getenv('SAVE_DOWNLOAD_DIRECTORY')
    local_zip_filename = os.getenv('LOCAL_ZIP_FILE_NAME')

    session = connect_to_server(key_path, hostname, port, username)
    try:
        zip_folder(session, remote_directory, remote_zip_filename)
        download_zip_folder(
            session,
            remote_zip_filename,
            save_download_directory,
            local_zip_filename,
        )
    finally:
        delete_zip_and_close(session, remote_zip_filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Backup Foundry CLI')
    parser.add_argument('config_file', help='Path to the configuration file')
    args = parser.parse_args()

    main(args)
