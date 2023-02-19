# speedTest
lauch speed test

# installation
```
sudo apt-get update
sudo apt-get upgrade -Y
sudo apt install apt-transport-https gnupg1 dirmngr lsb-release
curl -L https://packagecloud.io/ookla/speedtest-cli/gpgkey | gpg --dearmor | sudo tee /usr/share/keyrings/- - speedtestcli-archive-keyring.gpg >/dev/null
echo "deb [signed-by=/usr/share/keyrings/speedtestcli-archive-keyring.gpg] https://packagecloud.io/ookla/- - speedtest-cli/debian/ $(lsb_release -cs) main" | sudo tee  /etc/apt/sources.list.d/speedtest.list

-sudo apt update
-sudo apt install speedtest
```

### Automatic start of speedtest
```
sudo crontab -e
*/15 * * * *  python3 /home/pi/speedtest.py
```

### Setup MOre WIFI nodes
USe more than one Wifi connection so that the device can used easily in different homes. Look on the example.
[wpa_supllicant.conf](https://github.com/Chris-656/speedTest/wpa_supplicant.conf).
You can find the file here: /etc/wpa_supplicant/wpa_supplicant.conf.
