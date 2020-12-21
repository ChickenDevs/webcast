const auto = document.getElementById("auto");
const url = document.getElementById("url");
const urlTag = document.getElementById("urlTag");
const rtmpurl = document.getElementById("rtmpurl");
const rtmpurlTag = document.getElementById("rtmpurlTag");
const rtmpkey = document.getElementById("rtmpkey");
const rtmpkeyTag = document.getElementById("rtmpkeyTag");
const vbitrate = document.getElementById("vbitrate");
const vbitrateTag = document.getElementById("vbitrateTag");
const abitrate = document.getElementById("abitrate");
const abitrateTag = document.getElementById("abitrateTag");
const resolution = document.getElementById("resolution")
const videoDelay = document.getElementById("videoDelay")
const audioDelay = document.getElementById("audioDelay")
const volume = document.getElementById("volume")
const preset = document.getElementById("preset")
const submit = document.getElementById("submit")
const status_btn = document.getElementById("status")
const stop = document.getElementById("stop")
const start = document.getElementById("start")
const restart = document.getElementById("restart")
const output = document.getElementById("output")

const file = cockpit.file("/etc/webcast/webcast.conf", {syntax: JSON})

file.read()
.then((content, tag) => {
	try {
		if ('auto' in content) {
			if (content.auto == "true") {
				auto.checked = true
			} else {auto.checked = false}
		} else {auto.checked = true}
		set_auto()
		if ('url' in content) {
			url.value = content.url
		} else {url.value = "https://raw.githubusercontent.com/ChickenDevs/webcast/main/test-off.xml"}
		if ('rtmpurl' in content) {
			rtmpurl.value = content.rtmpurl
		}
		if ('rtmpkey' in content) {
			rtmpkey.value = content.rtmpkey
		}
		if ('vbitrate' in content) {
			vbitrate.value = content.vbitrate
		} else {vbitrate.value = 1250000}
		if ('abitrate' in content) {
			abitrate.value = content.abitrate
		} else {abitrate.value = 48000}
		if ('resolution' in content) {
			resolution.value = content.resolution
		} else {resolution.value = "1280x720"}
		if ('videoDelay' in content) {
			videoDelay.value = content.videoDelay
		} else {videoDelay.value = 0}
		if ('audioDelay' in content) {
			audioDelay.value = content.audioDelay
		} else {audioDelay.value = 1}
		if ('volume' in content) {
			volume.value = content.volume
		} else {volume.value = 0}
		if ('preset' in content) {
			preset.value = content.preset
		} else {preset.value = "veryfast"}
	} catch(err) {}
})
.catch(() => {})

function write() {
	try {
		const data = {
			auto: auto.checked.toString(),
			url: url.value,
			rtmpurl: rtmpurl.value,
			rtmpkey: rtmpkey.value,
			vbitrate: parseInt(vbitrate.value),
			abitrate: parseInt(abitrate.value),
			resolution: resolution.value,
			videoDelay: parseFloat(videoDelay.value),
			audioDelay: parseFloat(audioDelay.value),
			volume: parseInt(volume.value),
			preset: preset.value
		}
		console.log(data)
		file.replace(data)
		file.replace(data)
		.then(tag => {success()})
		.catch(err => {console.log(err); failure()})
	} catch(err) {
		failure()
		console.log(data)
	}
}

function success() {
	Toastify({
		text: "Success!",
		backgroundColor: "#00ff00"
	}).showToast();
}

function failure() {
	Toastify({
		text: "Failed!",
		backgroundColor: "#ff0000",
	}).showToast();
}

function service_ctl(action) {
	output.innerHTML = "";

        switch(action){
		case "stop":
			cockpit.spawn(["sudo", "pkill", "ffmpeg"])
			.then()
			cockpit.spawn(["sudo", "systemctl", "stop", "webcast.timer"])
			.then(success())
			break;
		case "start":
			cockpit.spawn(["sudo", "systemctl", "start", "webcast"])
			.stream(service_output)
			.then()
			cockpit.spawn(["sudo", "systemctl", "start", "webcast.timer"])
			.then(success())
			break;
		case "restart":
			cockpit.spawn(["sudo", "pkill", "ffmpeg"])
			.then()
			cockpit.spawn(["sudo", "systemctl", "restart", "webcast"])
			.stream(service_output)
			.then(success())
			break;
		default:
			cockpit.spawn(["sudo", "systemctl", "status", "webcast"])
			.stream(service_output)
			.then(success())
	}

	//.catch(err => {console.log(err)})
}

function service_output(data) {
	output.append(document.createTextNode(data));
}

function set_presets() {
	let veryfast = new Option("veryfast","veryfast");
	let faster = new Option("faster", "faster");
	let fast = new Option("fast", "fast");
	let medium = new Option("medium", "medium");
	if(resolution.value == "640x480"){
		while (preset.options.length > 2) {
			preset.remove(2)
		}
		preset.add(veryfast,undefined);
		preset.add(faster,undefined);
		preset.add(fast,undefined);
		preset.add(medium,undefined);
		preset.value = "fast";
	}
	if(resolution.value == "800x600") {
		while (preset.options.length > 2) {
			preset.remove(2)
		}
		preset.add(veryfast,undefined);
		preset.add(faster,undefined);
		preset.add(fast,undefined);
		preset.value = "faster";
	}
	if(resolution.value == "1280x720") {
		while (preset.options.length > 2) {
			preset.remove(2);
		}
		preset.add(veryfast,undefined);
		preset.add(faster,undefined);
		preset.value = "veryfast";
	} 
	if(resolution.value == "1920x1080") {
		while (preset.options.length > 2) {
			preset.remove(2);
		}
		preset.value = "superfast";
	}
}

function set_auto() {
	if(auto.checked == true){
		url.style.visibility = "visible"
		urlTag.style.visibility = "visible"
		rtmpurl.style.visibility = "hidden"
		rtmpurlTag.style.visibility = "hidden"
		rtmpkey.style.visibility = "hidden"
		rtmpkeyTag.style.visibility = "hidden"
		vbitrate.style.visibility = "hidden"
		vbitrateTag.style.visibility = "hidden"
		abitrate.style.visibility = "hidden"
		abitrateTag.style.visibility = "hidden"
	} else {
		url.style.visibility = "hidden"
		urlTag.style.visibility = "hidden"
		rtmpurl.style.visibility = "visible"
		rtmpurlTag.style.visibility = "visible"
		rtmpkey.style.visibility = "visible"
		rtmpkeyTag.style.visibility = "visible"
		vbitrate.style.visibility = "visible"
		vbitrateTag.style.visibility = "visible"
		abitrate.style.visibility = "visible"
		abitrateTag.style.visibility = "visible"
	}
}

set_presets();
set_auto();
resolution.addEventListener("change", set_presets);
auto.addEventListener("change", set_auto);
submit.addEventListener("click", write);
status_btn.addEventListener("click", () => {service_ctl("status")});
stop.addEventListener("click", () => {service_ctl("stop")});
start.addEventListener("click", () => {service_ctl("start")});
restart.addEventListener("click", () => {service_ctl("restart")});

