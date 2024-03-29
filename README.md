This is a custom streaming solution designed to work with the webcast system of The Church of Jesus Christ of Latter-day Saints. It uses Raspberry Pi 4, Ubuntu and ffmpeg to essentially replace the Teradek system. We initially started with Jeremy Willden's work on [OBS Automator](https://github.com/jeremywillden/obs-automator) but have since removed the requirement for OBS in order to make this as simple and automated as possible. (If anyone is interested in running OBS on a Pi we were successful at that and would be happy to share our experiences.)

App source code available at: https://github.com/ChickenDevs/webcast-app

# Webcast Quickstart
1. Download the [prebuilt image for a Raspberry Pi 4](https://github.com/ChickenDevs/webcast/releases).
2. Write the image to an SD card using the [Raspberry Pi Imager](https://www.raspberrypi.org/software/).
3. Install as shown below. Pictures are available in [the wiki](../../wiki/Images).
![Wiring Diagram](../../wiki/images/diagram.jpg)
4. We strongly recommend setting a static IP as shown [here](https://www.churchofjesuschrist.org/help/support/ip-assignment-page). The device name will be `webcast-pi` and the zone will be `public`.
![Technology Manager IP Assignment](../../wiki/images/tm-webcast-pi.jpg)
5. Point a web broswer to the IP address of the Pi after it boots from the SD card.
6. Login using webcast/alma3738
7. Go to the "Webcast Config" section of the Cockpit UI and enter the appropriate configuration information.
![Cockpit WebcastConfig Plugin](../../wiki/images/webcast_config.jpg)
8. Click submit to save the configuration.
9. Click start.

# Parts List
* [Raspberry Pi 4 - 4GB](https://www.amazon.com/dp/B07TC2BK1X)
* [Raspberry Pi 4 Armor Case with Dual Fan](https://www.amazon.com/dp/B07VD6LHS1)
* [Raspberry Pi 4 Power Supply](https://www.amazon.com/dp/B07TYQRXTK)
* [MicroSD card > 8Gb (Speed Class 10 recommended)](https://www.amazon.com/dp/B06XWN9Q99)
* [USB Sound Adapter](https://www.amazon.com/dp/B00IRVQ0F8)
* [3.5mm Audio Cable](https://www.amazon.com/dp/B088KLGVHJ)
* [USB Webcam (1080p, narrow FOV & Tripod mount recommended)](https://www.amazon.com/dp/B08931JJLV)
* [USB Extension Cable (as long as needed)](https://www.amazon.com/dp/B0777FDCX7)
* Tall camera mount (Tripod **OR** Clamp Mount for back of pew)
  * [Tall Tripod with standard camera mount](https://www.amazon.com/dp/B08D6KM95D)
  * [Clamp Mount (for back of pew)](https://www.amazon.com/gp/product/B0772LBG2D) **AND** [Selfie Stick](https://www.amazon.com/gp/product/B09688D5P9)
* [Gaffers Tape](https://www.amazon.com/gp/product/B01FZXLN5C) (if running cables across aisles)

These last two items are optional. We use the remote control outlet on the network switch to turn off/on the stream without having to reboot the Pi. You could use the power switch on the Pi directly or use the web interface to stop and start the stream from a smartphone, tablet or laptop. We chose the hanging remote control outlet with an indicator light so that it sat just above the floor where the bishopric could see the light and control it from their seats.
* [Remote Control Outlet](https://www.amazon.com/dp/B07WX2NBWR)
* [Ethernet switch (for wired networking)](https://www.amazon.com/dp/B0863M7C1L)

# FAQ
Q: Can I use wireless networking?
> A: Yes. In most of our buildings we are using wired networking so that we can shutoff the wireless if bandwidth becomes an issue. We do have one branch which is using rented space without wired networking so we are successfully using wireless networking there. To setup wirless networking you will either need access to the console of the Pi or you can connect the Pi to a wired network with a DHCP server to setup the wireless networking. Connect to the management interface through the wired interface and on the "Terminal" section run `sudo nmtui` and then select "Activate a Connection" to setup the SSID and password.

Q: Can I use this on something besides a Raspberry Pi?
> A: Yes. This will work anywhere ffmpeg works, so pretty much everywhere. It will require some modifcation to the way USB devices are identified in the ffmpeg command. We have successfully used the same logic in a PowerShell script during our investigations but never completed the automation (which would use scheduled tasks in Windows) and therefore haven't released that code. Any Linux device that uses v4l2 and alsa should just work but hasn't been tested.

Q: Can I use this to stream to services other than the webcast system?
> A: Yes. On the "Webcast Config" section of the management interface you can choose not to use AutoConfig at which point you will be able to manually set the rtmp URL, streamkey, video bitrate and audio bitrate to match any service that accepts an rtmp stream. This has been tested with YouTube, Facebook and Twitch.

Q: Can I use this on low bandwidth connections?
> A: Yes. We have one building with a 500kbps upload which is using this solution successfully. The configuration page allows the selection of camera resolutions of 640x480, 800x600, 1280x720 or 1920x1080. Using the camera from the parts list above we have tested many of the supported webcast encoder settings from 640x480@250kbps to 1920x1080@2000kpbs.
