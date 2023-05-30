const base64Images = document.querySelectorAll('.base64-image');
base64Images.forEach((element) => {
    const base64 = element.getAttribute('data-base64');
    const imgElement = document.createElement('img');
    imgElement.src = base64;
    element.appendChild(imgElement);
});