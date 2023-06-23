if command -v zip >/dev/null 2>&1; then
    echo "zip is already installed."
else
    # Install zip
    sudo apt-get install zip
fi

cd Cameraman/output

zip -r $1.zip $1