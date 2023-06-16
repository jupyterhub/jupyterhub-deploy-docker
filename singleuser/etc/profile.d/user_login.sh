# Get GMAP user (latest) README file
#
if [ ! -f "${HOME}/README.md" ];
then
  wget -q -O ${HOME}/README.md \
    https://raw.githubusercontent.com/europlanet-gmap/.github/main/profile/README.md
fi
