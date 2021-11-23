# Home Assistant Tapo P100 Control
A custom integration for home assistant to control the Tapo P100 plugs

## Installation

To install the Tapo P100 integration:

1) copy the `tapo_p100_control` folder into the `custom_components` folder on your home assistant instance.
`custom_components` folder should be where your configuration.yaml file is.\
It could be in: `/home/pi/.homeassistant/`\
If you have home assistant supervised (using docker) it could be in: `/usr/share/hassio/homeassistant/`.\
In this case you can enter with ssh and do:\
`cd /usr/share/hassio/homeassistant/`\
`ls`\
if the `custom_components` doesn't exist:
```
sudo mkdir custom_components
cd custom_components
sudo git clone https://github.com/fishbigger/HomeAssistant-Tapo-P100-Control.git
sudo mv HomeAssistant-Tapo-P100-Control/tapo_p100_control/ .
sudo rm -r HomeAssistant-Tapo-P100-Control/
cd tapo_p100_control
pwd
```
Now you will see:\
`/usr/share/hassio/homeassistant/custom_components/tapo_p100_control`


2) **restart** Home Assistant

3) add these lines to your `configuration.yaml` file after you setup the Tapo app (`ip_address` can be found after you choose  the device in the app, press the Gear in upper right and choose `Device Info`):

```yaml

#P100 or P105 Plug
switch:
    platform: tapo_p100_control
    ip_address: 192.168.x.x
    email: email@gmail.com
    password: Password123
    
#L510 Series Bulbs
light:
    platform: tapo_p100_control
    ip_address: 192.168.x.x
    email: email@gmail.com
    password: Password123
```

4) **restart** Home Assistant **again**

5) You should see no issues in Home Assistant `Configuration`, `Logs`\
If there are issues with Credentials you should:\
    a) Change your password to 8 chars through the app (from Tapo app home screen, press Me at bottom right, press your email, `Change Password`)\
    b) LOG OUT from the app and log in\
    c) Restart Home Assistant and see the Configuration, Logs again.

6) Test your plug:\
    a) Go to `Developer Tools`, `Services` tab\
    b) Search `Switch: Turn On` and `Pick entity: tapo plug router` and `Call Service`. It should Turn on the plug (you can also check the `States` tab).

7) Create basic automation:\
    a) Go to `Configuration`, `Automations`, `Add Automation`, give a name\
    b) at `Triggers` choose `Time pattern`, `seconds 40` (leave the other empty)\
    c) at `Actions` choose the same as before: (Search `Switch: Turn On` and `Pick entity: tapo plug router`)\
    d) Save. Now, at every 40 seconds (e.g. 15:20:40, 15:21:40) the plug will turn on. Enjoy

8) In order to add 2 plugs, take a look [here.](https://github.com/fishbigger/HomeAssistant-Tapo-P100-Control/issues/32#issuecomment-886623693)

9) Add them to your `Overview` by pressing the three dots at upper right corner, `Edit Dashboard`, press `ADD CARD` button, choose `By entity` tab and search `switch`.


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change

## Upcoming Features:
* Support for L530 Colour Bulbs
* UI setup integration
* Uploading to HACS

## Contributors
* [K4CZP3R](https://github.com/K4CZP3R)
* [Extreeeme](https://github.com/Extreeeme)


## License
[MIT](https://choosealicense.com/licenses/mit/)
