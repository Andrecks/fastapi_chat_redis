        // Send message
        const messageBox = document.getElementById('message');
        document.getElementById('sendButton').addEventListener('click', sendMessage);
        messageBox.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                sendMessage();
                event.preventDefault();  // Prevent form submission
            }
        });

        function sendMessage() {
            socket.send(messageBox.value);
            messageBox.value = '';
        }