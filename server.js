const express = require('express');
const app = express();
const http = require('http').createServer(app);
const io = require('socket.io')(http, { cors: { origin: "*" } });

app.use(express.json());

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html');
});

app.post('/webhook', (req, res) => {
    io.emit('new_signal', req.body);
    res.sendStatus(200);
});

const PORT = process.env.PORT || 3000;
http.listen(PORT, () => {
    console.log('Server is running...');
});
