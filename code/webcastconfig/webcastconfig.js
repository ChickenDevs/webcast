const url = document.getElementById("url");
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
		if ('url' in content) {
			url.value = content.url
		} else {url.value = "https://raw.githubusercontent.com/ChickenDevs/webcast/main/test-off.xml"}
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
			url: url.value,
			videoDelay: parseFloat(videoDelay.value),
			audioDelay: parseFloat(audioDelay.value),
			volume: parseInt(volume.value),
			preset: preset.value
		}
		file.replace(data)
		.then(tag => {console.log(tag)})
		.catch(err => {console.log(err); failure()})
		success()
	} catch(err) {
		failure()
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
	let input
	if (action === "status" || action === "restart") {
		input = ["sudo", "systemctl", action, "webcast"]
	} else { input = ["sudo", "systemctl", action, "webcast.timer"]}

	output.innerHTML = "";

	cockpit.spawn(input)
	.stream(service_output)
	.then(success())
	.catch(err => {console.log(err)})
}

function service_output(data) {
	output.append(document.createTextNode(data));
}

submit.addEventListener("click", write);
status_btn.addEventListener("click", () => {service_ctl("status")});
stop.addEventListener("click", () => {service_ctl("stop")});
start.addEventListener("click", () => {service_ctl("start")});
restart.addEventListener("click", () => {service_ctl("restart")});

cockpit.transport.wait(() => {});
