import paramiko
import os
from dotenv import load_dotenv
from paramiko.rsakey import RSAKey
import subprocess


class Runner:

    def __init__(self, ssh_key_path, instance_ip):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_key_path = ssh_key_path
        self.instance_ip = instance_ip

    def connect(self):
        print("Connecting to instance with IP: " + self.instance_ip + " and SSH key: " + self.ssh_key_path)
        try:
            key = RSAKey.from_private_key_file(os.path.expanduser(self.ssh_key_path))
            self.client.connect(hostname=self.instance_ip, username="ubuntu", pkey=key)
            print("Connected successfully!")
            if self.transfer_scripts():
                print("Scripts transferred successfully!")
                self.run_loop()
            else:
                print("Error transferring remote_scripts.")
        except Exception as e:
            print("Error connecting to instance: " + str(e))
        finally:
            self.client.close()

    def transfer_scripts(self):
        sftp = self.client.open_sftp()
        try:
            sftp.put("./remote_scripts/init.sh", "/home/ubuntu/init.sh")
            sftp.put("./remote_scripts/train.sh", "/home/ubuntu/train.sh")
            sftp.put("./remote_scripts/run.sh", "/home/ubuntu/run.sh")
            sftp.put("./remote_scripts/save.sh", "/home/ubuntu/save.sh")
            sftp.put("./remote_scripts/clear.sh", "/home/ubuntu/clear.sh")
            return True
        except Exception as e:
            print("Error transferring remote_scripts: " + str(e))
            return False
        finally:
            sftp.close()

    def run_loop(self):
        while True:
            user_input = input("Enter command: ")

            user_input_parts = user_input.split(" ")
            if len(user_input_parts) == 0:
                print("Please enter a command.")
                continue

            command = user_input_parts[0]
            match command:
                case "i":
                    if len(user_input_parts) == 3:
                        branch = user_input_parts[1]
                        commit = user_input_parts[2]
                        self.init_model(branch, commit)
                    elif len(user_input_parts) == 2:
                        branch = user_input_parts[1]
                        self.init_model(branch)
                    else:
                        print("Please enter a branch name and commit hash")
                case "t": self.train_model()
                case "lm": print("Command not implemented yet.")
                case "li": print("Command not implemented yet.")
                case "r": self.run_model()
                case "s":
                    if len(user_input_parts) != 2:
                        print("Please enter a name for the model.")
                        continue
                    self.save_model(user_input_parts[1])
                case "c": self.connect_to_remote_terminal()

    def init_model(self, branch, commit=None):
        try:
            stdout = None
            stderr = None
            if commit is not None:
                _, stdout, stderr = self.client.exec_command(f"source init.sh {branch} {commit}")
            else:
                _, stdout, stderr = self.client.exec_command(f"source init.sh {branch}")

            for line in stdout:
                print(line.strip())

            exit_status = stdout.channel.recv_exit_status()
            if exit_status == 0:
                print("Model is inited successfully.")
            else:
                print("Model init failed.")
                for line in stderr:
                    print(line.strip())
        except Exception as e:
            print("Error initializing model: " + str(e))

    def train_model(self):
        channel = None
        try:
            channel = self.client.invoke_shell()

            channel.send('source train.sh\n')

            while not channel.exit_status_ready():
                if channel.recv_ready():
                    output = channel.recv(1024).decode().strip()
                    print(output)
                    if "~/Cameraman" in output:
                        print("Training complete!")
                        break
        except Exception as e:
            print("Error training model: " + str(e))
        finally:
            if channel is not None:
                channel.close()

    def run_model(self):
        channel = None
        try:
            channel = self.client.invoke_shell()

            channel.send('source run.sh\n')

            while not channel.exit_status_ready():
                if channel.recv_ready():
                    output = channel.recv(1024).decode().strip()
                    print(output)
                    if "~/Cameraman" in output:
                        print("Running complete!")
                        break

            self.copy_image_output()
            self.clear_image_output()
        except Exception as e:
            print("Error running model: " + str(e))
        finally:
            if channel is not None:
                channel.close()

    def copy_image_output(self):
        subprocess.call(
            f'source ./local_scripts/copy_image_output.sh {self.ssh_key_path} {self.instance_ip}',
            shell=True
        )

    def clear_image_output(self):
        try:
            _, stdout, stderr = self.client.exec_command(f"source clear.sh")
            exit_status = stdout.channel.recv_exit_status()
            if exit_status == 0:
                print("Image output is cleared.")
            else:
                print("Image output clearing failed.")
                for line in stderr:
                    print(line.strip())
        except Exception as e:
            print("Error clearing image output: " + str(e))
        finally:
            print("Image output cleared.")

    def save_model(self, name):
        if self.zip_model_on_remote_machine(name):
            print("Model zipped successfully.")
            sftp = None
            try:
                sftp = self.client.open_sftp()
                sftp.get(
                    f"/home/ubuntu/Cameraman/output/{name}.zip", os.path.expanduser(f'~/Desktop/{name}.zip'),
                    callback= lambda transferred, total: print(f"Transferred: {transferred}, Total: {total}")
                )
                print("Model saved successfully.")
                return True
            except Exception as e:
                print("Error saving model: " + str(e))
                return False
            finally:
                sftp.close()
        else:
            print("Model is not saved.")

    def zip_model_on_remote_machine(self, name):
        try:
            _, stdout, stderr = self.client.exec_command(f"source save.sh {name}")
            for line in stdout:
                print(line.strip())
            exit_status = stdout.channel.recv_exit_status()
            if exit_status == 0:
                print("Model zipepd successfully.")
            else:
                print("Model zipping failed.")
                for line in stderr:
                    print(line.strip())
            return exit_status == 0
        except Exception as e:
            print("Error zipping model: " + str(e))
            return False

    def connect_to_remote_terminal(self):
        print("Connecting to SSH...")
        subprocess.call(f'source ./local_scripts/connect.sh {self.ssh_key_path} {self.instance_ip}', shell=True)


if __name__ == "__main__":
    load_dotenv()

    sshKeyPath = os.getenv("SSH_KEY_PATH")
    if sshKeyPath is None:
        print("Please set the SSH_KEY_PATH environment variable.")
        exit(1)

    instanceIp = os.getenv("INSTANCE_IP")
    if instanceIp is None:
        print("Please set the INSTANCE_IP environment variable.")
        exit(1)

    runner = Runner(os.getenv("SSH_KEY_PATH"), os.getenv("INSTANCE_IP"))
    runner.connect()
