const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode');
const mongoose = require('mongoose');
const fs = require('fs');
const path = require('path');

// Connect to the first MongoDB database (Whatsapp)
const whatsappDb = mongoose.createConnection('mongodb://localhost:27017/whatsapp', {
    useNewUrlParser: false,
    useUnifiedTopology: false,
});

// Example of using the connections:
whatsappDb.once('open', () => {
    console.log('Connected to Whatsapp database');
});

const messageSchema = new mongoose.Schema({
    messageId: String, // Added messageId field
    from: String,
    notifyName: String,
    body: String,
    timestamp: Number,
    isForwarded: Boolean,
    mediaPath: String,
    isFromUser: Boolean,
    feedback: { type: Boolean, default: true }, // Added feedback field with default value true
});

const Message = whatsappDb.model('messages', messageSchema); // for whatsappDb

const updatesSchema = new mongoose.Schema({
    message_id: String,      // Reference to the message ID
    isPending: Boolean,      // Indicates if the update is pending
    update_type: String      // Type of update (e.g., "feedback")
});

const Update = whatsappDb.model('updates', updatesSchema); // Create 'updates' collection

const client = new Client({
    authStrategy: new LocalAuth(), // Enable LocalAuth for persistent sessions
});

const qrImagePath = path.join(__dirname, 'qr-code.png');

client.on('ready', () => {
    console.log('WhatsApp client is ready!');

    // Delete QR code file when the client is ready
    if (fs.existsSync(qrImagePath)) {
        fs.unlink(qrImagePath, (err) => {
            if (err) {
                console.error('Error deleting QR code file:', err);
            } else {
                console.log('QR code file deleted successfully.');
            }
        });
    }

    watchTodoList(); // Start watching tasks
});

// Event: Generate QR Code
client.on('qr', (qr) => {
    qrcode.toFile(qrImagePath, qr, (err) => {
        if (err) {
            console.error('Error generating QR code:', err);
        } else {
            console.log(`QR code saved to ${qrImagePath}`);
        }
    });
});

// Event: Client Authentication Failure
client.on('auth_failure', (msg) => {
    console.error('Authentication failed:', msg);
});

// Event: Client Disconnected
client.on('disconnected', (reason) => {
    console.log('Client disconnected:', reason);
});

// Event: Incoming message
client.on('message', async (message) => {

    if (message.body.charAt(0) !== '✽') {
        console.log(`Received message: ${message.body}`);

        const msgData = {
            messageId: message.id.id, // Save message ID
            from: message.from,
            notifyName: message._data.notifyName || 'Unknown',
            body: message.body,
            timestamp: message.timestamp,
            isForwarded: message.isForwarded || false,
            isFromUser: false,
            feedback: true // Added feedback field with default value true
        };

        if (message.hasMedia) {
            const media = await message.downloadMedia();
            const mediaPath = path.join(__dirname, 'media', `${message.id.id}.${media.mimetype.split('/')[1]}`);
            fs.writeFileSync(mediaPath, media.data, 'base64');
            msgData.mediaPath = mediaPath;
        }

        const newMessage = new Message(msgData);
        await newMessage.save();
        console.log('Incoming message saved to database.');
    }
    else {
        console.log('Message starts with "%". Skipping operation.');
    }
});

// Event: Outgoing message
client.on('message_create', async (message) => {

    if (message.body === '👍' || message.body === '👎') {
        try {
            const quotedMessage = await message.getQuotedMessage(); // Get quoted message
            const quotedMessageText = quotedMessage.body.split('\n')[0].slice(1); // Remove first character and get the first line
            const quotedMessageId = quotedMessageText; // Treat the extracted text as messageId

            // Find the corresponding document in the messages database
            const doc = await Message.findOne({ messageId: quotedMessageId });

            if (doc) {
                // Update feedback based on thumbs up or thumbs down
                const feedbackValue = message.body === '👍';
                doc.feedback = feedbackValue;
                await doc.save();
                console.log(`Updated feedback for messageId ${quotedMessageId} to ${feedbackValue}.`);

                // Add a document to the 'updates' collection
                const updateData = {
                    message_id: quotedMessageId,
                    isPending: false,
                    update_type: 'feedback'
                };
                const newUpdate = new Update(updateData);
                await newUpdate.save();
                console.log(`Added feedback update to 'updates' collection for messageId ${quotedMessageId}.`);
            } else {
                console.error(`No document found for messageId ${quotedMessageId}.`);
            }
        } catch (err) {
            console.error('Error processing thumbs feedback:', err);
        }
    }
    else if (message.body.charAt(0) !== '✽') {
        if (message.fromMe) {
            console.log(`User message: ${message.body}`);
            const msgData = {
                messageId: message.id.id, // Save message ID
                from: message.from,
                notifyName: 'User',
                body: message.body,
                timestamp: message.timestamp,
                isForwarded: message.isForwarded || false,
                isFromUser: true,
                feedback: true
            };

            if (message.hasMedia) {
                const media = await message.downloadMedia();
                const mediaPath = path.join(__dirname, 'media', `${message.id.id}.${media.mimetype.split('/')[1]}`);
                fs.writeFileSync(mediaPath, media.data, 'base64');
                msgData.mediaPath = mediaPath;
            }

            const newMessage = new Message(msgData);
            await newMessage.save();
            console.log('User message saved to database.');
        }
    } else {
        console.log('Message starts with "%". Skipping operation.');
    }
});

// Event: Cleanup on process exit
process.on('exit', () => {
    if (fs.existsSync(qrImagePath)) {
        fs.unlinkSync(qrImagePath);
        console.log('QR code file deleted on process exit.');
    }
});

// Optional: Handle termination signals (e.g., Ctrl+C)
process.on('SIGINT', () => {
    console.log('Process terminated (SIGINT).');
    if (fs.existsSync(qrImagePath)) {
        fs.unlinkSync(qrImagePath);
        console.log('QR code file deleted on SIGINT.');
    }
    process.exit();
});
const todoDb = mongoose.createConnection('mongodb://localhost:27017/TODOBOT', {
    useNewUrlParser: true,  // Use proper URL parser
    useUnifiedTopology: true,  // Use unified topology
});

// Log when connected
todoDb.once('open', () => {
    console.log('Connected to TODOLIST database');
});

// Define the schema based on the structure of the existing collection
const todoListSchema = new mongoose.Schema({
    message_id: String, // Added message_id field at the beginning
    category: String,
    title: String,
    description: String,
    due_date: Date,
    priority: String,
    status: String,
    created_at: Date,
    modified_at: Date,
    remainder_system: String,
    is_human: Boolean,
    is_notified: Boolean,
    next_notification_slot: Date, // Added next_notification_slot field at the end
});

const Todo = todoDb.model('Todo', todoListSchema, 'TODOLIST');

/**
 * Function to format task details into a WhatsApp-friendly message
 * @param {Object} task - Task document
 * @returns {string} - Formatted task message
 */

function formatTaskMessage(task) {
    return `✽${task.message_id}` +
        `\n\n*New Task Added:*\n\n` +
        `*Category:*\n ${task.category}\n\n` +
        `*Title:*\n ${task.title}\n\n` +
        `*Description:*\n ${task.description}\n\n` +
        `*Due Date:*\n ${task.due_date}\n\n` +
        `*Priority:*\n ${task.priority}\n\n` +
        `*Status:* ${task.status}`;
}

/**
 * Function to monitor the TODO list collection for new tasks
 */
async function watchTodoList() {
    console.log('Started watching TODO list for new tasks...');
    setInterval(async () => {
        try {
            console.log('Checking for new tasks...');
            // const newTasks = await Todo.find({ is_notified: false });
            const newTasks = await Todo.find({ is_notified: false });

            console.log(newTasks)
            for (const task of newTasks) {
                const taskMessage = formatTaskMessage(task);
                const userChatId = '917667634519@c.us'; // Replace with the correct chat ID
                await client.sendMessage(userChatId, taskMessage);
                console.log(`Task notification sent for task: ${task.title}`);

                // Mark task as notified
                task.is_notified = true;
                await task.save();
            }
        } catch (err) {
            console.error('Error watching TODO list:', err);
        }
    }, 5000); // Poll every 5 seconds
}

client.initialize();