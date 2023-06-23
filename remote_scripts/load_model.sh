# Check if unzip is already installed
if command -v unzip >/dev/null 2>&1; then
    echo "unzip is already installed."
else
    # Install unzip
    sudo apt-get install unzip
fi

