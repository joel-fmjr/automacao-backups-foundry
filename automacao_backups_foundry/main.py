import os

import paramiko
from decouple import config


def connect_to_server(key_path, hostname, port, username):
    session = paramiko.SSHClient()
    session.load_system_host_keys()
    session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    private_key = paramiko.RSAKey.from_private_key_file(key_path)
    session.connect(hostname, port, username, pkey=private_key)
    return session


def zip_folder(session, remote_directory, remote_zip_filename):
    zip_command = ' '.join(['zip -r ', remote_zip_filename, remote_directory])
    _, stdout, _ = session.exec_command(zip_command)
    stdout.read()


def download_zip_folder(
    session, remote_zip_filename, local_directory, local_zip_filename
):
    sftp = session.open_sftp()
    sftp.get(
        remote_zip_filename, os.path.join(local_directory, local_zip_filename)
    )
    sftp.close()


def delete_zip_and_close(session, remote_zip_filename):
    session.exec_command('rm ' + remote_zip_filename)
    session.close()


if __name__ == '__main__':
    key_path = config('KEY_PATH')
    hostname = config('HOSTNAME')
    port = config('PORT')
    username = config('USERNAME')
    remote_directory = config('REMOTE_DIRECTORY')
    remote_zip_filename = config('REMOTE_ZIP_FILENAME')
    local_directory = config('LOCAL_DIRECTORY')
    local_zip_filename = config('LOCAL_ZIP_FILENAME')

    session = connect_to_server(key_path, hostname, port, username)
    zip_folder(session, remote_directory, remote_zip_filename)
    download_zip_folder(
        session, remote_zip_filename, local_directory, local_zip_filename
    )
    delete_zip_and_close(session, remote_zip_filename)
