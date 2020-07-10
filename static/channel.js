document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    socket.on('connect', () => {
        document.getElementById('button').forEach(button => {
            button.onclick = () => {
                newMessage = document.getElementById('textbox').value;
                author = '{{ username }}';
                socket.emit('new message', {'message': newMessage, 'author': author, 'channel':channelName});
            };
        });
    });
    socket.on('messages updated', data => {
        window.location.reload(True);
    });
});
