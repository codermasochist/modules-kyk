#!/bin/bash

# Получаем текущую рабочую директорию
WORKING_DIR=$(pwd)

runin() {
	# Runs the arguments, piping stderr to logfile
	{ "$@" 2>>"${WORKING_DIR}/hikka-install.log" || return $?; } | while read -r line; do
		printf "%s\n" "$line" >>"${WORKING_DIR}/hikka-install.log"
	done
}

runout() {
	# Runs the arguments, piping stderr to logfile
	{ "$@" 2>>"${WORKING_DIR}/hikka-install.log" || return $?; } | while read -r line; do
		printf "%s\n" "$line" >>"${WORKING_DIR}/hikka-install.log"
	done
}

errorin() {
	cat "${WORKING_DIR}/hikka-install.log"
}
errorout() {
	cat "${WORKING_DIR}/hikka-install.log"
}

##############################################################################

clear

printf "\n\e[1;35;47m                   \e[0m"
printf "\n\e[1;35;47m █ █ █ █▄▀ █▄▀ ▄▀█ \e[0m"
printf "\n\e[1;35;47m █▀█ █ █ █ █ █ █▀█ \e[0m"
printf "\n\e[1;35;47m                   \e[0m"
printf "\n\n\e[3;34;40m Installing...\e[0m\n\n"

##############################################################################

printf "\r\033[0;34mPreparing for installation...\e[0m"

# Удалено создание и изменение владельца файла hikka-install.log

if [ -d "Hikka/hikka" ]; then
	cd Hikka || {
		printf "\rError: Install git package and re-run installer"
		exit 6
	}
	DIR_CHANGED="yes"
fi
if [ -f ".setup_complete" ]; then
	# If hikka is already installed by this script
	PYVER="3.10"
	printf "\rExisting installation detected. Hikka is already installed.\n"
fi

##############################################################################

echo "Preparing installation..." >"${WORKING_DIR}/hikka-install.log"

PYVER="3.10" # Стандартная версия Python

##############################################################################

printf "\r\033[K\033[0;32mPreparation complete!\e[0m"
printf "\n\r\033[0;34mCloning repo...\e[0m"

##############################################################################

rm -rf "${WORKING_DIR}/Hikka"
runout git clone https://github.com/hikariatama/Hikka/ "${WORKING_DIR}/Hikka" || {
	errorout "Clone failed."
	exit 3
}
cd "${WORKING_DIR}/Hikka" || {
	printf "\r\033[0;33mRun: \033[1;33mpkg install git\033[0;33m and restart installer"
	exit 7
}

printf "\r\033[K\033[0;32mRepo cloned!\e[0m"
printf "\n\r\033[0;34mCreating config.json...\e[0m"

# Создаем файл config.json внутри папки Hikka
cat > "${WORKING_DIR}/Hikka/config.json" <<EOL
{
    "api_id": 7301124,
    "api_hash": "46eb50618e7a00ca8b165275d9e0fe0b",
    "app_name": "Discipulus Pietas Omnis"
}
EOL

printf "\r\033[K\033[0;32mconfig.json created!\e[0m"
printf "\n\r\033[0;34mInstalling python dependencies...\e[0m"

runin python$PYVER -m pip install --upgrade pip setuptools wheel --user
runin python$PYVER -m pip install -r requirements.txt --upgrade --user --no-warn-script-location --disable-pip-version-check || {
	errorin "Requirements failed!"
	exit 4
}
rm -f "${WORKING_DIR}/hikka-install.log"
touch "${WORKING_DIR}/.setup_complete"

printf "\r\033[K\033[0;32mDependencies installed!\e[0m"
printf "\n\033[0;32mHikka installation complete! To start it, run: python$PYVER -m hikka\e[0m\n\n"
