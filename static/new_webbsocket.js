const socket = new WebSocket(`ws://localhost:8000/ws?nickname=${nickname}`);

socket.onmessage = function(event) {
    console.log(`[message] Data received from server: ${event.data}`);
    const chatbox = document.getElementById('chatbox');
    const memberList = document.getElementById('memberList'); // Get the member list element
    const newMessage = document.createElement('div');
    newMessage.classList.add('chat-message');

    if (event.data.startsWith('user_list:')) {
        const userList = event.data.split(':')[1];
        const users = userList.split(',');

        // Clear the existing member list
        memberList.innerHTML = '';

        users.forEach(function(username) {
            const listItem = document.createElement('li');
            listItem.textContent = username;
            memberList.appendChild(listItem);
        });
    } else if (event.data.split(':')[1].startsWith('base64')) {
        const username = event.data.split(':')[0];
        const base64 = event.data.split(',')[1];
        const usernameElement = document.createElement('p');
        usernameElement.textContent = username;
        newMessage.appendChild(usernameElement);
        const imageElement = document.createElement('img');
        imageElement.src = `data:image/png;base64,${base64}`;
        newMessage.appendChild(imageElement);
    } else {
        const textElement = document.createElement('p');
        textElement.textContent = event.data;
        newMessage.appendChild(textElement);
    }
    
    chatbox.appendChild(newMessage);
    chatbox.scrollTop = chatbox.scrollHeight;
    // Handle incoming messages from the server
    // You can update the chatbox or perform other actions here
};
