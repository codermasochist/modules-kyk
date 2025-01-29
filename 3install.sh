#!/bin/bash

WORKING_DIR=$(pwd)

runin() {
	{ "$@" 2>>"${WORKING_DIR}/heroku-install.log" || return $?; } | while read -r line; do
		printf "%s\n" "$line" >>"${WORKING_DIR}/heroku-install.log"
	done
}

runout() {
	{ "$@" 2>>"${WORKING_DIR}/heroku-install.log" || return $?; } | while read -r line; do
		printf "%s\n" "$line" >>"${WORKING_DIR}/heroku-install.log"
	done
}

errorin() {
	cat "${WORKING_DIR}/heroku-install.log"
}
errorout() {
	cat "${WORKING_DIR}/heroku-install.log"
}

SUDO_CMD=""
if [ ! x"$SUDO_USER" = x"" ]; then
	if command -v sudo >/dev/null; then
		SUDO_CMD="sudo -u $SUDO_USER "
	fi
fi

clear
clear

printf "\n\e[1;35;47m                   \e[0m"
printf "\n\e[1;35;47m █ █ █ █▄▀ █▄▀ ▄▀█ \e[0m"
printf "\n\e[1;35;47m █▀█ █ █ █ █ █ █▀█ \e[0m"
printf "\n\e[1;35;47m                   \e[0m"
printf "\n\n\e[3;34;40m Installing...\e[0m\n\n"

printf "\r\033[0;34mPreparing for installation...\e[0m"

if [ -d "Heroku/heroku" ]; then
	cd Heroku || {
		printf "\rError: Install git package and re-run installer"
		exit 6
	}
	DIR_CHANGED="yes"
fi
if [ -f ".setup_complete" ]; then
	PYVER="3.10"
	printf "\rExisting installation detected. Heroku is already installed.\n"
fi

echo "Preparing installation..." >"${WORKING_DIR}/heroku-install.log"

PYVER="3.10"

printf "\r\033[K\033[0;32mPreparation complete!\e[0m"
printf "\n\r\033[0;34mCloning repo...\e[0m"

${SUDO_CMD}rm -rf "${WORKING_DIR}/Heroku"
runout ${SUDO_CMD}git clone https://github.com/coddrago/Heroku/ "${WORKING_DIR}/Heroku" || {
	errorout "Clone failed."
	exit 3
}
cd "${WORKING_DIR}/Heroku" || {
	printf "\r\033[0;33mRun: \033[1;33mpkg install git\033[0;33m and restart installer"
	exit 7
}

printf "\r\033[K\033[0;32mRepo cloned!\e[0m"
printf "\n\r\033[0;34mCreating config.json...\e[0m"

cat > "${WORKING_DIR}/Heroku/config.json" <<EOL
{
    "api_id": 7301124,
    "api_hash": "46eb50618e7a00ca8b165275d9e0fe0b",
    "app_name": "Discipulus Pietas Omnis"
}
EOL

printf "\r\033[K\033[0;32mconfig.json created!\e[0m"
printf "\n\r\033[0;34mInstalling python dependencies...\e[0m"

runin "$SUDO_CMD python$PYVER" -m pip install --upgrade pip setuptools wheel --user
runin "$SUDO_CMD python$PYVER" -m pip install -r requirements.txt --upgrade --user --no-warn-script-location --disable-pip-version-check || {
	errorin "Requirements failed!"
	exit 4
}
rm -f "${WORKING_DIR}/heroku-install.log"
touch "${WORKING_DIR}/.setup_complete"

printf "\r\033[K\033[0;32mDependencies installed!\e[0m"
printf "\n\033[0;32mHeroku installation complete! To start it, run: python$PYVER -m heroku\e[0m\n\n"
