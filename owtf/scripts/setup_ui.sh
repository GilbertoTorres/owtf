#!/usr/bin/env bash
#
# This script install the node dependencies listed in package.json and build the bundle file using webpack.

# bring in the color variables: `normal`, `info`, `warning`, `danger`, `reset`
cd $(dirname "$0");SCRIPT_DIR=`pwd -P`;cd $OLDPWD
. $SCRIPT_DIR/common.sh

# Download community written templates for export report functionality.

if [ ! -d "${1}/webui/src/Report/templates" ]; then
    echo "${warning} Templates not found, fetching the latest ones...${reset}"
    git clone https://github.com/owtf/templates.git "$1/webui/src/Report/templates"
else
    echo "${info}[*] Templates directory found. Nothing done.${reset}"
fi
if [ ! -z "${OWTF_DEV}" ]; then
    echo "OWTF_DEV is set, building the bundle"
    # Instead of using apt-get to install npm we will nvm to install npm because apt-get installs older-version of node
    echo "${normal}[*] Installing npm using nvm.${reset}"
    wget https://raw.githubusercontent.com/creationix/nvm/v0.31.1/install.sh -O /tmp/install_nvm.sh
    bash /tmp/install_nvm.sh
    rm -rf /tmp/install_nvm.sh

    # Setup nvm and install node
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"  # This loads nvm
    nvm install node
    nvm alias default node
    echo "${normal}[*] npm successfully Installed.${reset}"

    # Installing webpack and gulp globally so that it can used by command line to build the bundle.
    npm install -g yarn
    # Installing node dependencies
    echo "${normal}[*] Installing node dependencies.${reset}"
    cd $1/webui
    yarn
    echo "${normal}[*] Dependencies successfully Installed.${reset}"

    # Bulding the ReactJS project
    echo "${normal}[*] Building using webpack.${reset}"
    yarn build
    echo "${normal}[*] Build successful${reset}"
else
    echo "${normal}[*] Variable OWTF_DEV is not set, using the bundled assets${reset}"
fi
