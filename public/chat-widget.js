class ChatWidget {
    constructor() {
        // Initialize session ID
        this.sessionId = localStorage.getItem('chatSessionId');
        if (!this.sessionId) {
            this.sessionId = this.generateSessionId();
            localStorage.setItem('chatSessionId', this.sessionId);
        }
        
        this.isOpen = false;
        this.createWidget();
        this.attachEventListeners();
        this.loadChatHistory();
        
        // Listen for logout event
        window.addEventListener('userLoggedOut', this.handleLogout.bind(this));
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    async loadChatHistory() {
        try {
            const response = await fetch(`http://localhost:5000/chat/history/${this.sessionId}`);
            const data = await response.json();
            
            if (data.history) {
                // Clear existing messages
                const messagesContainer = document.getElementById('rakk-chat-messages');
                messagesContainer.innerHTML = '';
                
                // Add messages in chronological order
                data.history.reverse().forEach(msg => {
                    this.addMessage('user', msg.user_message);
                    this.addMessage('bot', msg.bot_response, JSON.parse(msg.product_links || '[]'));
                });
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }

    createWidget() {
        // Create main container
        const container = document.createElement('div');
        container.id = 'rakk-chat-widget';
        container.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
        `;

        // Create chat icon button
        const chatButton = document.createElement('button');
        chatButton.id = 'rakk-chat-button';
        chatButton.innerHTML = '💬';
        chatButton.style.cssText = `
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: #FA5252;
            border: none;
            color: white;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 2px 10px rgba(250, 82, 82, 0.3);
            transition: transform 0.2s ease;
        `;
        chatButton.onmouseover = () => chatButton.style.transform = 'scale(1.1)';
        chatButton.onmouseout = () => chatButton.style.transform = 'scale(1)';

        // Create chat window
        const chatWindow = document.createElement('div');
        chatWindow.id = 'rakk-chat-window';
        chatWindow.style.cssText = `
            display: none;
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: 350px;
            height: 500px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(250, 82, 82, 0.2);
            flex-direction: column;
        `;

        // Create chat header
        const chatHeader = document.createElement('div');
        chatHeader.style.cssText = `
            padding: 15px;
            background: #FA5252;
            color: white;
            border-radius: 10px 10px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        `;
        chatHeader.innerHTML = `
            <span>RakkGears Assistant</span>
            <button id="rakk-chat-close" style="background: none; border: none; color: white; cursor: pointer; font-size: 20px;">×</button>
        `;

        // Create chat messages container
        const chatMessages = document.createElement('div');
        chatMessages.id = 'rakk-chat-messages';
        chatMessages.style.cssText = `
            flex-grow: 1;
            padding: 15px;
            overflow-y: auto;
            background: #fff;
        `;

        // Create chat input container
        const chatInput = document.createElement('div');
        chatInput.style.cssText = `
            padding: 15px;
            border-top: 1px solid #f0f0f0;
            display: flex;
            gap: 10px;
            background: #fff;
        `;

        // Create message input
        const messageInput = document.createElement('input');
        messageInput.type = 'text';
        messageInput.id = 'rakk-chat-input';
        messageInput.placeholder = 'Type your message...';
        messageInput.style.cssText = `
            flex-grow: 1;
            padding: 10px;
            border: 1px solid #f0f0f0;
            border-radius: 20px;
            outline: none;
            transition: border-color 0.2s ease;
        `;
        messageInput.onfocus = () => messageInput.style.borderColor = '#FA5252';

        // Create send button
        const sendButton = document.createElement('button');
        sendButton.innerHTML = 'Send';
        sendButton.style.cssText = `
            padding: 8px 20px;
            background: #FA5252;
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            transition: background-color 0.2s ease;
        `;
        sendButton.onmouseover = () => sendButton.style.background = '#e63e3e';
        sendButton.onmouseout = () => sendButton.style.background = '#FA5252';

        // Assemble the widget
        chatInput.appendChild(messageInput);
        chatInput.appendChild(sendButton);
        chatWindow.appendChild(chatHeader);
        chatWindow.appendChild(chatMessages);
        chatWindow.appendChild(chatInput);
        container.appendChild(chatButton);
        container.appendChild(chatWindow);
        document.body.appendChild(container);
    }

    attachEventListeners() {
        const chatButton = document.getElementById('rakk-chat-button');
        const chatWindow = document.getElementById('rakk-chat-window');
        const closeButton = document.getElementById('rakk-chat-close');
        const sendButton = chatWindow.querySelector('button');
        const messageInput = document.getElementById('rakk-chat-input');

        chatButton.addEventListener('click', () => this.toggleChat());
        closeButton.addEventListener('click', () => this.toggleChat());
        sendButton.addEventListener('click', () => this.sendMessage());
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
    }

    toggleChat() {
        const chatWindow = document.getElementById('rakk-chat-window');
        this.isOpen = !this.isOpen;
        chatWindow.style.display = this.isOpen ? 'flex' : 'none';
        
        // Load chat history when opening the chat
        if (this.isOpen) {
            this.loadChatHistory();
        }
    }

    async sendMessage() {
        const messageInput = document.getElementById('rakk-chat-input');
        const message = messageInput.value.trim();
        
        if (!message) return;

        // Add user message to chat
        this.addMessage('user', message);
        messageInput.value = '';

        try {
            const response = await fetch('http://localhost:5000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId
                })
            });

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            // Add bot response to chat with product links
            this.addMessage('bot', data.response, data.product_links);
        } catch (error) {
            console.error('Error:', error);
            this.addMessage('bot', 'Sorry, I encountered an error. Please try again.');
        }
    }

    addMessage(type, content, productLinks = null) {
        const messagesContainer = document.getElementById('rakk-chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.style.cssText = `
            margin-bottom: 10px;
            padding: 10px 15px;
            border-radius: 15px;
            max-width: 80%;
            ${type === 'user' ? 
                'background: #FA5252; color: white; margin-left: auto;' : 
                'background: #f8f9fa; color: #333; margin-right: auto; border: 1px solid #f0f0f0;'}
        `;

        // Add message content
        messageDiv.textContent = content;

        // Add product links if available and not empty
        if (type === 'bot' && productLinks && productLinks.length > 0) {
            const linksDiv = document.createElement('div');
            linksDiv.style.cssText = `
                margin-top: 10px;
                padding-top: 10px;
                border-top: 1px solid #eee;
            `;
            
            const linksTitle = document.createElement('div');
            linksTitle.textContent = 'Recommended Products:';
            linksTitle.style.cssText = `
                font-weight: bold;
                margin-bottom: 5px;
                color: #FA5252;
            `;
            linksDiv.appendChild(linksTitle);

            productLinks.forEach(link => {
                const linkElement = document.createElement('a');
                linkElement.href = link.url;
                linkElement.textContent = link.name;
                linkElement.style.cssText = `
                    display: block;
                    color: #FA5252;
                    text-decoration: none;
                    padding: 5px 0;
                    transition: color 0.2s ease;
                `;
                linkElement.onmouseover = () => linkElement.style.color = '#e63e3e';
                linkElement.onmouseout = () => linkElement.style.color = '#FA5252';
                linksDiv.appendChild(linkElement);
            });

            messageDiv.appendChild(linksDiv);
        }

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    async handleLogout() {
        try {
            const sessionId = localStorage.getItem('chatSessionId');
            if (sessionId) {
                // Clear chat history from database
                const response = await fetch('/api/chat/logout', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ session_id: sessionId })
                });

                if (!response.ok) {
                    console.error('Failed to clear chat history');
                }

                // Clear local storage
                localStorage.removeItem('chatSessionId');
                
                // Clear chat messages
                this.messagesContainer.innerHTML = '';
                
                // Reset session ID
                this.sessionId = null;
            }
        } catch (error) {
            console.error('Error during logout:', error);
        }
    }
}

// Initialize the chat widget when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ChatWidget();
}); 