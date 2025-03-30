import subprocess

class PowerShellDirectory:
    def __init__(self, module_path, root_path):
        # Set the path to the PowerShell module and root directory
        self.module_path = module_path
        self.root_path = root_path

    def run_powershell_script(self, script):
        """Run PowerShell script and return the output."""
        command = ["powershell", "-ExecutionPolicy", "ByPass", "-Command", script]
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            return result.stdout
        else:
            print("Error:", result.stderr)
            return None

    def get_directory_contents(self):
        """Get the directory contents by running PowerShell code."""
        # PowerShell script to import the module and create a Directory object
        script = f"""
        Import-Module '{self.module_path}'
        $directory = [Directory]::new('{self.root_path}')
        $directory.PrintContents()
        """
        return self.run_powershell_script(script)

    def get_directory_summary(self):
        """Get a summary of the directory."""
        script = f"""
        Import-Module '{self.module_path}'
        $directory = [Directory]::new('{self.root_path}')
        $directory.ToString()
        """
        return self.run_powershell_script(script)

# Example usage:
# module_path = 'C:\\path\\to\\your\\directory.psm1'  # Path to the PowerShell module
# root_path = 'C:\\path\\to\\your\\root\\directory'

# ps_directory = PowerShellDirectory(module_path, root_path)

# # Print the directory contents
# print(ps_directory.get_directory_contents())

# # Get a summary of the directory
# print(ps_directory.get_directory_summary())
