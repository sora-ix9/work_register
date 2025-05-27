const FPS = 5;
const video = document.getElementById("video");
let canvas1 = document.getElementById("canvas1");
let context1 = canvas1.getContext("2d");
let camera_permission = false;
// let detected_img_count = 0;
// let raw_img_count = 0;

function arrayBuffer_to_str(buffer, encoding='utf-8') {
  const decoder = new TextDecoder(encoding);

  return decoder.decode(buffer);
}

function confirm_no() {
  confirm_img_elem.setAttribute("src", detected_img_url);
  register_time = arrayBuffer_to_str(registerTime_arrBuffer)

  document.getElementById("register_time_elem").innerHTML = register_time;
  document.getElementById("db_recording_noti").innerHTML = "";
}

function confirm_yes() {
  fetch(confirm_img_elem.src)
    .then(res => res.arrayBuffer())
    .then(img_arrBuffer => {
      socket.emit('confirm_yes', [img_arrBuffer, register_time]); // Send via WebSocket
    })

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
  window.socket = io.connect(location.protocol + "//" + document.domain + ":" + location.port, {transports: [ "websocket" ]});
  
  console.log("Clinent is connecting to server: ", window.socket.connected, 'sid: ', window.socket.id, 'transport: ', window.socket.io.engine.transport.name);
}

window.socket.on("detected_img", (data) => {
  img_arrBuffer = data[0];
  registerTime_arrBuffer = data[1];

  bin_detected_img = new Blob([img_arrBuffer]);
  detected_img_url = URL.createObjectURL(bin_detected_img);
  detected_img_elem.setAttribute("src", detected_img_url);
  
  if (confirm_img_elem.getAttribute("src") == null) {
    confirm_img_elem.setAttribute("src", detected_img_url);
  }
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
    context1.drawImage(video, 0, 0, width, height);

    canvas1.toBlob(blob => {
        const reader = new FileReader();
        reader.onload = function(e) {
          const arrayBuffer = e.target.result;
          window.socket.emit('raw_img', arrayBuffer);
        };
        reader.readAsArrayBuffer(blob);
    }, 'image/jpeg');

    // raw_img_count += 1
    // console.log("2. raw_img_count =", raw_img_count);
  }
}, 1000 / FPS);