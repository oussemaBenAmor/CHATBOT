// Chat functionality for AI Transaction Assistant

class ChatApp {
    constructor() {
        this.chatContainer = document.getElementById('chatContainer');
        this.questionInput = document.getElementById('questionInput');
        this.fileInput = document.getElementById('fileInput');
        this.fileStatus = document.getElementById('fileStatus');
        this.sendButton = document.getElementById('sendButton');
        this.isProcessing = false;
        
        this.initializeEventListeners();
        this.focusInput();
    }

    initializeEventListeners() {
        // File input handling
        this.fileInput.addEventListener('change', () => this.handleFileSelection());
        
        // Send button click
        this.sendButton.addEventListener('click', () => this.handleSendClick());
        
        // Enter key handling
        this.questionInput.addEventListener('keypress', (e) => this.handleKeyPress(e));
        
        // Input focus for better UX
        this.questionInput.addEventListener('focus', () => this.handleInputFocus());
        this.questionInput.addEventListener('blur', () => this.handleInputBlur());
    }

    handleFileSelection() {
        if (this.fileInput.files.length > 0) {
            const fileName = this.fileInput.files[0].name;
            this.fileStatus.textContent = `📎 File selected: ${fileName}`;
            this.fileStatus.classList.add('show');
            
            // Add visual feedback
            this.addFilePreview(fileName);
        } else {
            this.fileStatus.classList.remove('show');
        }
    }

    addFilePreview(fileName) {
        // Remove existing preview
        const existingPreview = document.querySelector('.file-preview');
        if (existingPreview) {
            existingPreview.remove();
        }

        // Create file preview element
        const preview = document.createElement('div');
        preview.className = 'file-preview';
        preview.innerHTML = `
            <div class="file-preview-content">
                <i class="fas fa-file-alt"></i>
                <span>${fileName}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="remove-file">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        // Insert before file status
        this.fileStatus.parentNode.insertBefore(preview, this.fileStatus);
    }

    handleSendClick() {
        if (!this.isProcessing && this.questionInput.value.trim()) {
            this.sendMessage();
        }
    }

    handleKeyPress(e) {
        if (e.key === 'Enter' && !e.shiftKey && !this.isProcessing) {
            e.preventDefault();
            this.sendMessage();
        }
    }

    handleInputFocus() {
        this.questionInput.parentElement.style.transform = 'scale(1.02)';
    }

    handleInputBlur() {
        this.questionInput.parentElement.style.transform = 'scale(1)';
    }

    async sendMessage() {
        const question = this.questionInput.value.trim();
        if (!question || this.isProcessing) return;

        this.setProcessingState(true);

        // Add user message
        this.addMessage('user', question);
        
        // Show typing indicator
        this.showTypingIndicator();

        // Clear input and file status
        this.questionInput.value = '';
        this.fileStatus.classList.remove('show');
        this.removeFilePreview();

        try {
            const formData = new FormData();
            formData.append('question', question);
            if (this.fileInput.files.length > 0) {
                formData.append('file', this.fileInput.files[0]);
                this.fileInput.value = '';
            }

            const response = await fetch('/chat', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            // Hide typing indicator
            this.hideTypingIndicator();

            if (response.ok) {
                this.addMessage('bot', data.answer, data);
                this.showSuccessFeedback();
            } else {
                this.addMessage('bot', data.answer || 'An error occurred. Please try again.');
                this.showErrorFeedback();
            }
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('bot', 'Network error. Please check your connection and try again.');
            this.showErrorFeedback();
        } finally {
            this.setProcessingState(false);
        }
    }

    setProcessingState(processing) {
        this.isProcessing = processing;
        this.sendButton.disabled = processing;
        
        if (processing) {
            this.sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            this.sendButton.classList.add('loading');
        } else {
            this.sendButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
            this.sendButton.classList.remove('loading');
        }
    }

    addMessage(type, content, data = null) {
        const messageRow = document.createElement('div');
        messageRow.className = `message-row ${type}`;

        const messageBubble = document.createElement('div');
        messageBubble.className = 'message-bubble';

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';

        if (type === 'bot' && data) {
            // Add transaction info if available
            if (data.transaction_type) {
                const transactionInfo = this.createTransactionInfo(data);
                messageContent.appendChild(transactionInfo);
            }

            // Add the main answer
            const answerText = document.createElement('div');
            answerText.className = 'answer-content';
            answerText.innerHTML = content.replace(/\n/g, '<br>');
            messageContent.appendChild(answerText);
        } else {
            messageContent.textContent = content;
        }

        const messageMeta = this.createMessageMeta(type);
        messageBubble.appendChild(messageContent);
        messageBubble.appendChild(messageMeta);
        messageRow.appendChild(messageBubble);
        this.chatContainer.appendChild(messageRow);

        // Remove welcome message after first interaction
        this.removeWelcomeMessage();

        // Scroll to bottom with smooth animation
        this.scrollToBottom();
    }

    createTransactionInfo(data) {
        const transactionInfo = document.createElement('div');
        transactionInfo.className = 'transaction-info';
        
        //const confidenceBadge = data.confidence ? 
            //`<span class="confidence-badge">Confidence: ${(data.confidence * 100).toFixed(0)}%</span>` : '';
        
        const sentencesCount = data.relevant_sentences_count ? 
            `<p>Found ${data.relevant_sentences_count} relevant information pieces</p>` : '';
        
        const urlsProcessed = data.urls_processed ? 
            `<p><i class="fas fa-globe"></i> Processed ${data.urls_processed} website(s)</p>` : '';
        
        // Add enhanced URL processing indicator
        const urlProcessingInfo = data.urls_processed ? 
            `<p><i class="fas fa-search"></i> Extracted detailed conditions from websites</p>` : '';
        
        transactionInfo.innerHTML = `
            <h4><i class="fas fa-info-circle"></i> Transaction Type: ${data.transaction_type.charAt(0).toUpperCase() + data.transaction_type.slice(1)}</h4>
            
            ${sentencesCount}
            ${urlsProcessed}
            ${urlProcessingInfo}
        `;
        
        return transactionInfo;
    }

    createMessageMeta(type) {
        const messageMeta = document.createElement('div');
        messageMeta.className = 'message-meta';
        messageMeta.innerHTML = `
            <span>${type === 'user' ? 'You' : 'AI Assistant'}</span>
            <span>${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
        `;
        return messageMeta;
    }

    removeWelcomeMessage() {
        const welcomeMessage = document.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.style.opacity = '0';
            welcomeMessage.style.transform = 'translateY(-20px)';
            setTimeout(() => welcomeMessage.remove(), 300);
        }
    }

    showTypingIndicator() {
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        typingIndicator.innerHTML = `
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        typingIndicator.id = 'typingIndicator';
        this.chatContainer.appendChild(typingIndicator);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.style.opacity = '0';
            setTimeout(() => typingIndicator.remove(), 300);
        }
    }

    removeFilePreview() {
        const filePreview = document.querySelector('.file-preview');
        if (filePreview) {
            filePreview.remove();
        }
    }

    scrollToBottom() {
        this.chatContainer.scrollTo({
            top: this.chatContainer.scrollHeight,
            behavior: 'smooth'
        });
    }

    showSuccessFeedback() {
        this.sendButton.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
        setTimeout(() => {
            this.sendButton.style.background = 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)';
        }, 1000);
    }

    showErrorFeedback() {
        this.sendButton.style.background = 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
        setTimeout(() => {
            this.sendButton.style.background = 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)';
        }, 1000);
    }

    focusInput() {
        this.questionInput.focus();
    }
}

// Quick action functions
function askQuickQuestion(question) {
    if (window.chatApp) {
        window.chatApp.questionInput.value = question;
        window.chatApp.sendMessage();
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatApp = new ChatApp();
});

// Add some additional utility functions
function addQuickAction(question) {
    const quickActions = document.querySelector('.quick-actions');
    if (quickActions) {
        const action = document.createElement('div');
        action.className = 'quick-action';
        action.textContent = question;
        action.onclick = () => askQuickQuestion(question);
        quickActions.appendChild(action);
    }
}

// Export for potential external use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChatApp;
}
