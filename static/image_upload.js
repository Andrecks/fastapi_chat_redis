function uploadImage() {
    const inputElement = document.getElementById('imageInput');
    const file = inputElement.files[0];
  
    const reader = new FileReader();
    reader.onloadend = function () {
      const base64String = reader.result.split(',')[1];
  
      const imageObject = {
        type: 'image',
        base64: base64String,
      };
  
      const jsonData = JSON.stringify(imageObject);
      socket.send(jsonData); // Send jsonData to the WebSocket server
    };
  
    reader.readAsDataURL(file);
  }
  
  const uploadButton = document.getElementById('uploadButton');
  uploadButton.addEventListener('click', uploadImage);