Two-Factor-Security-Door
========================

> Robynn Tournemine | September 13th, 2022

------------------------

It is about a connected door that opens using a Raspberry Pi 4 B that will be configured by exploiting a database and linking a touchscreen to an RFID scanner. The RFID will allow to trigger a python script with a magnetized badge. This will then ask the user to enter his PIN code on the touchscreen allowing him to open the door. The concept of double authentication will therefore be used. This door was made for a school project.


Table of Contents
------------------------
  1. [Installation](#installation)
  2. [My Hardware list](#my-hardware-list)
  3. [My Software list](#my-software-list)
  4. [Electronic schematic](#electronic-schematic)
  5. [Software installation procedure](#software-installation-procedure)
      - [Operating System](#operating-system)
      - [Activating SSH](#activating-ssh)
      - [Activating VNC](#activating-vnc)
      - [Display and touchscreen setup](#display-and-touchscreen-setup)
      - [PhpMyAdmin setup](#phpmyadmin-setup)
      - [Adding a user in the phpMyAdmin DataBase](#adding-a-user-in-the-phpmyadmin-database)
      - [RFID reader setup](#rfid-reader-setup)
      - [Launching the script at startup](#launching-the-script-at-startup)
  6. [Usage](#usage)


Installation
------------------------
  Clone the repository
  ```
  git clone https://github.com/RobynnTournemine/Two-Factor-Security-Door.git/
  ```
  
  Install all required packages with pip3
  ```
  cd Two-Factor-Security-Door/
  pip3 install -r requirements.txt
  ```

My Hardware list
------------------------
  - Raspberry Pi 4 model B 4GB
  - Raspberry Pi 7 inch touchscreen | Model ID : 2473872
  - RFID Reader | Model ID : MFRC522
  - Relay module
  - Electrical strike
  - 32GB SD card
  - Keyboard/Mouse
  - A 12v power supply (for the electrical strike)
  - A 5v power suplay (for the Raspberry Pi)


My Software list
------------------------
  - Raspberry Pi OS (32bits)
  - Apache2
  - PhpMyAdmin
  - VNC/SSH
  - WinSCP


Electronic schematic
------------------------
![image](https://user-images.githubusercontent.com/89530375/189650726-6f6e69ba-2351-4326-a054-d8f9426fda5c.png)


Software installation procedure
------------------------
### Operating System
  Installation of the Raspberry Pi OS (32bits, Desktop) on the SD card using the [`Raspberry Pi Imager`](https://www.raspberrypi.com/software/)

### Activating SSH
  1. Enable ``SSH`` to start it automatically at startup
  ```
  sudo systemctl enable ssh
  ```
  2. Start ``SSH``
  ```
  sudo systemctl start ssh
  ```

### Activating VNC
  1. Go to Menu > Preferences > Raspberry Pi Configuration > Interfaces > enable ``VNC``
  2. Update the packages
  ```
  sudo apt update
  ```
  3. Install ``realvnc-vnc-viewer``
  ```
  sudo apt install realvnc-vnc-viewer
  ```
  5. Install [`VNC viewer`](https://www.realvnc.com/en/connect/download/viewer/) on the remote workstation 


###  Display and touchscreen setup
  1. Comment out the driver ``dtoverlay=vc4-kms-v3d`` in the ``/boot/config.txt`` file
  2. Add the line ``display_rotate=1`` in the end of the same file
  3. Install xinput to adjust the touchscreen
  ```
  sudo apt install xinput
  ```
  4. Add the execute permission to the bash script
  ```
  sudo chmod +x touchscreen.sh
  ```
  5. Edit the ``/etc/profile`` file in superuser by adding in the last line ``sudo /your/script/path/touchscreen.sh``

### PhpMyAdmin setup
  1. Install ``Apache2`` with the required utils
  ```
  sudo apt install apache2 apache2-utils -y
  ```
  2. Install the ``PHP`` module from ``Apache2``
  ```
  sudo apt install libapache2-mod-php -y
  ```
  3. Install ``MariaDB Server``
  ```
  sudo apt install mariadb-server -y
  ```
  4. Install ``phpMyAdmin`` without forgetting to select ``Apache2`` during the installation
  ```
  sudo apt install phpMyAdmin -y
  ```
  5. Connect to the ``MySQL`` server
  ```
  sudo mysql
  ```
  6. Create a ``username`` based on the username of your system 
  ```
  CREATE USER 'username'@'localhost' IDENTIFIED BY 'username';
  ```
  7. Give all privileges to the newly created user
  ```
  GRANT ALL PRIVILEGES ON *.* TO 'username'@'localhost';
  ```
  8. Access to the phpMyAdmin panel with the created user by going on http://*your-rpi-ip-address*/phpmyadmin
  9. Creation of a DataBase named ``door_lock``
  10. Import the tables from the DB by dragging the file [`door_lock.sql`](https://github.com/RoobyCH/Two-Factor-Security-Door/blob/main/door_lock.sql) into the DB ``door_lock``

### Adding a user in the phpMyAdmin DataBase
  1. In the DB ``door_lock``, select the ``access_list`` table
  2. Under the "Insert" tab, add the necessary information in each column:
      - ``user_id``: enter a non-existent ID for the user
      - ``name``: enter the firstname/name of the user
      - ``image``: enter the name of the file which must be in ``.gif``, format 300x300 px then the file must be in the same directory as the script [`lock.py`](https://github.com/RoobyCH/Two-Factor-Security-Door/blob/main/lock.py) (if your image is named ``image.gif``, then you have to enter ``image``)
      - ``rfid_code``: write to a new badge using the [`Write.py`](https://github.com/RoobyCH/Two-Factor-Security-Door/blob/main/pi-rfid/Write.py) script, read it using the [`Read.py`](https://github.com/RoobyCH/Two-Factor-Security-Door/blob/main/pi-rfid/Write.py) script and then enter the given RFID badge code
      - ``pin``: enter the user's PIN code to unlock the door
  3. Click on "Execute" at the bottom right
  4. Check that the user has been added to the table in the "Browse" tab

### RFID reader setup
  1. Open the RPi configuration menu
  ```
  sudo raspi-config
  ```
  2. Select 3 Interface Options > I4 SPI > Yes
  3. Check that the ``RFID`` reader is detected 
  ```
  lsmod | grep spi
  ```
  ![RFID_Reader](https://user-images.githubusercontent.com/89530375/189689854-8a4a204e-c424-4d94-beaf-da4becc9197f.png)

### Launching the script at startup
  1. Go to the ``LXDE-pi`` directory
  ```
  cd ~/.config/lxsession/LXDE-pi
  ```
  2. Open/Create the file ``autostart`` with a superuser privilege
  ```
  sudo nano autostart
  ```
  3. Insert the following lines:
  ```
  @lxpanel --profile LXDE-pi
  @pcmanfm --desktop --profile LXDE-pi
  @xscreensaver -no-splash
  @sudo python lock.py
  ```


Usage
------------------------
To use the Two-Factor-Security-Door, you must have an RFID badge that has been configured and added to the database. This badge will allow the system to recognize you as the person with the access rights to unlock the door.

The procedure is as follows:
  1. Take your ``RFID`` badge
  2. Place your badge on the ``RFID`` reader
  3. Enter your PIN code on the system display on the secured door
  4. Open the door


------------------------
S/O to [**@WarToky**](https://github.com/WarToky) who collaborate with me for this project and [**@NoblePierre**](https://github.com/NoblePierre) who helped me to do the Python code
