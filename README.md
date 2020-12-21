This is a custom streaming solution designed to work with the webcast system of The Church of Jesus Christ of Latter-Day Saints. It uses Raspberry Pi 4, Ubuntu and ffmpeg to essentially replace the Teradek system. We initally started with Jeremy Willden's work on [OBS Automater](https://github.com/jeremywillden/obs-automator) but have sinced removed the requirement for OBS in order to make this as simple and automated as possible. (If anyone is interested in running OBS on a Pi we were successful at that and would be happy to share our experiences.)

# Webcast Quickstart
1. Download the [prebuilt image for a Raspberry Pi 4](https://github.com/ChickenDevs/webcast/releases/download/v1.0.0/webcast-ffmpeg-pi4.img.gz).
2. Write the image to an SD card using the [Raspberry Pi Imager](https://www.raspberrypi.org/software/).
3. Point a web broswer to the IP address of the Pi after it boots from the SD card.
4. Login using webcast/alma3738
5. Go to the "Webcast Config" section of the Cockpit UI and enter the appropriate configuration information.
6. Click submit to save the configuration.
7. Click start.

# Parts List
* [Raspberry Pi 4 - 4GB](https://www.amazon.com/dp/B07TC2BK1X)
* [Raspberry Pi 4 Armor Case with Dual Fan](https://www.amazon.com/dp/B07VD6LHS1)
* [Raspberry Pi 4 Power Supply](https://www.amazon.com/dp/B07TYQRXTK)
* [MicroSD card > 8Gb (Speed Class 10 recommended)](https://www.amazon.com/dp/B06XWN9Q99)
* [USB Sound Adapter](https://www.amazon.com/dp/B00IRVQ0F8)
* [USB Webcam (1080p, narrow FOV & Tripod mount recommended)](https://www.amazon.com/dp/B08931JJLV)
* [USB Extension Cable (as long as needed)](https://www.amazon.com/dp/B0777FDCX7)
* [Tall Tripod with standard camera mount](https://www.amazon.com/dp/B08D6KM95D)

These last two items are optional. We use the remote control outlet on the network switch to turn off/on the webcast without having to reboot the Pi. You could use the power switch on the Pi directly or use the web interface to stop and start the stream from a smartphone, tablet or laptop.
* [Remote Control Outlet](https://www.amazon.com/dp/B07D2BY7VY)
* [Ethernet switch (for wired networking)](https://www.amazon.com/dp/B000FNFSPY)

# FAQ
Q: Can I use wireless networking?
> A: Yes. In most of our buildings we are using wired networking so that we can shutoff the wireless if bandwidth becomes an issue. We do have one branch which is using rented space without wired networking so we are successfully using wireless networking there. To setup wirless networking you will need to connect the Pi to a wired network with a DHCP server to setup the wireless networking. Connect to the management interface through the wired interface and on the "Terminal" section run "sudo nmtui" and then select "Activate a Connection" to setup the SSID and password.

Q: Can I use this on something besides a Raspberry Pi?
> A: Yes. This will work anywhere ffmpeg works, so pretty much everywhere. It will require some modifcation to the way USB devices are identified in the ffmpeg command. We have successfully used the same logic in a PowerShell script during our investigations but never completed the automation (which would use scheduled tasks in Windows) and therefore haven't released that code. Any Linux device that uses v4l2 and alsa should just work but hasn't been tested.

Q: Can I use this to stream to services other than the webcast system?
> A: Yes. On the "Webcast Config" section of the management interface you can choose not to use AutoConfig at which point you will be able to manually set the rtmp URL, streamkey, video bitrate and audio bitrate to match any service that accepts an rtmp stream. This has been tested with YouTube, Facebook and Twitch.
