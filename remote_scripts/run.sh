cd Cameraman
source venv/bin/activate
python inference.py

if command -v zip >/dev/null 2>&1; then
    echo "zip is already installed."
else
    # Install zip
    sudo apt-get install zip
fi

zip -r image_output.zip image_output