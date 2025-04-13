class Directory {
    [string]$Path
    [string]$Name
    [bool]$IsDirectory
    [array]$Files
    [array]$Subdirectories

    Directory([string]$path) {
        $this.Path = $path
        $this.Name = (Get-Item $path).Name
        $this.IsDirectory = (Test-Path $path -PathType Container)
        $this.Files = @()
        $this.Subdirectories = @()

        if ($this.IsDirectory) {
            $this._PopulateContents()
        }
    }

    [void] _PopulateContents() {
        $items = Get-ChildItem -Path $this.Path
        foreach ($item in $items) {
            if ($item.PSIsContainer) {
                $this.Subdirectories += [Directory]::new($item.FullName)
            } else {
                $this.Files += $item.Name
            }
        }
    }

    [void] PrintContents([int]$level = 0) {
        $indent = '  ' * $level
        Write-Host "$indent Directory: $($this.Name)"
        foreach ($file in $this.Files) {
            Write-Host "$indent  File: $file"
        }
        foreach ($subdir in $this.Subdirectories) {
            $subdir.PrintContents($level + 1)
        }
    }

    [string] ToString() {
        return "Directory: $($this.Name), Path: $($this.Path), Files: $($this.Files.Count), Subdirectories: $($this.Subdirectories.Count)"
    }
}

Export-ModuleMember -Function * -Alias *
