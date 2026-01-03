const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.json());
app.use(express.static(__dirname));

// Սա բացում է քո index.html-ը
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Սա ստանում է սիգնալը TradingView-ից
app.post('/webhook', (req, res) => {
    console.log('Signal received:', req.body);
    io.emit('new_signal', req.body);
    res.sendStatus(200);
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log('Server is running on port ' + PORT));
