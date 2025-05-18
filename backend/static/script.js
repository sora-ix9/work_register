const FPS = 5;
const video = document.getElementById("video");
let canvas1 = document.getElementById("canvas1");
let context = canvas1.getContext("2d");
let camera_permission = false;
// let detected_img_count = 0;
// let raw_img_count = 0;

function confirm_no() {
  confirm_img_elem.setAttribute("src", detected_img_URL);
  register_time = atob(base64str_register_time);
  document.getElementById("register_time_elem").innerHTML = register_time;
  document.getElementById("db_recording_noti").innerHTML = "";
}

function confirm_yes() {
  window.socket.emit("confirm_yes", confirm_img_elem.src + "," + btoa(register_time));
  document.getElementById("db_recording_noti").innerHTML = "The choosen image is successfully registered to database.";
}

function update_camera_permision() {
  navigator.mediaDevices.enumerateDevices()
  .then(devices => {
    devices.forEach(device => {
      if (device.kind == "videoinput" && device.label == "Integrated Webcam") {
        camera_permission = true;
      }
      else {
        camera_permission = false;
      }
    });
  });
}

if (!window.socket) {

  window.socket = io.connect(location.protocol + "//" + document.domain + ":" + location.port);

  window.socket.on("connect", function () {
    console.log("Clinent is connecting to server: ", window.socket.connected, 'sid: ', window.socket.id);
  });

  window.socket.on("disconnect", function () {
    console.log("Disconnected from server");
  });
}

window.socket.on("detected_img", (detectedImg_registerTime_URL) => {
  detected_img_URL = detectedImg_registerTime_URL.split(",")[0] + "," + detectedImg_registerTime_URL.split(",")[1]; // Extract data url contained only the base64 string of detected image (the base64 string of register time is deleted off). 
  base64str_register_time = detectedImg_registerTime_URL.split(",")[2];
  detected_img_elem.setAttribute("src", detected_img_URL);

  if (confirm_img_elem.getAttribute("src") == null) {
    confirm_img_elem.setAttribute("src", detected_img_URL);
  }

  // detected_img_count += 1
  // console.log("1. detected_img_count =", detected_img_count);
});

// Get video from media device and then display it onto the video element. 
if (navigator.mediaDevices.getUserMedia){
	navigator.mediaDevices
  .getUserMedia({ video: true })
  .then((stream) => {
    video.srcObject = stream;
		video.play();
  });
}

setInterval(() => {
  update_camera_permision();
  if (camera_permission) {
    width = video.width;
    height = video.height;
    context.drawImage(video, 0, 0, width, height);
    let imgData = canvas1.toDataURL("image/jpeg", 0.5);
    context.clearRect(0, 0, width, height);
    window.socket.emit("raw_img", imgData);

    // raw_img_count += 1
    // console.log("2. raw_img_count =", raw_img_count);
  }
}, 1000 / FPS);