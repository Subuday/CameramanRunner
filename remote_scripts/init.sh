# Check if pyenv is already installed
if [ -x "/home/ubuntu/.pyenv/bin/pyenv" ]; then
    echo "pyenv is already installed."
else
    sudo apt-get update; sudo apt-get install -y --assume-yes make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

    # Install pyenv
    curl https://pyenv.run | bash

    # Add pyenv initialization to the shell profile
    echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
    echo 'eval "$(pyenv init -)"' >> ~/.bashrc
    echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc

    # Source the shell profile
    source ~/.bashrc

    echo "pyenv has been installed successfully."
fi

rm -rf Cameraman
git clone https://github.com/Subuday/Cameraman.git
cd Cameraman
git checkout $1
if [ -n "$2" ]; then
  git reset --hard $2
fi

if ! pyenv versions --bare | grep -q 3.10.10; then
    pyenv install 3.10.10
else
    pyenv local 3.10.10
fi

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt