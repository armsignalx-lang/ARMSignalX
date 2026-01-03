const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.json());
app.use(express.static(__dirname));

// Հիմնական էջը բացելու համար
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// TradingView Webhook-ի համար
app.post('/webhook', (req, res) => {
    console.log('Ստացված սիգնալ:', req.body);
    io.emit('new_signal', req.body);
    res.sendStatus(200);
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log('Server is running on port ' + PORT));
