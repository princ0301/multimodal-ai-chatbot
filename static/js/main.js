document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.getAttribute('data-tab');
            
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            tabContents.forEach(tab => tab.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const clearButton = document.getElementById('clear-button');
    const toneSelector = document.getElementById('tone-selector');
    const micButton = document.getElementById('mic-button');
    const imageButton = document.getElementById('image-button');
    const imageInput = document.getElementById('image-input');
    const audioInput = document.getElementById('audio-input');
    
    let isRecording = false;
    let mediaRecorder = null;
    let audioChunks = [];
    let selectedImage = null;
    
    async function sendMessage() {
        const message = userInput.value.trim();
        
        if (!message && !selectedImage && !isRecording) {
            return;
        }
        
        addMessageToChat('user', message);
        
        if (selectedImage) {
            const img = document.createElement('img');
            img.src = URL.createObjectURL(selectedImage);
            img.className = 'user-image';
            
            const lastMessage = chatMessages.lastElementChild;
            lastMessage.querySelector('.message-content').appendChild(img);
        }
        
        const loadingMessage = addMessageToChat('assistant', 'Thinking...');
        const loadingElement = loadingMessage.querySelector('.message-content p');
        
        const formData = new FormData();
        formData.append('message', message);
        formData.append('tone', toneSelector.value);
        
        if (selectedImage) {
            formData.append('image', selectedImage);
        }
        
        try {
            const response = await fetch('/send_message', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            loadingElement.textContent = data.ai_response;
            
            userInput.value = '';
            selectedImage = null;
            
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
        } catch (error) {
            loadingElement.textContent = 'Sorry, an error occurred. Please try again.';
            console.error('Error:', error);
        }
    }
 
    function addMessageToChat(role, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const paragraph = document.createElement('p');
        paragraph.textContent = text;
        
        contentDiv.appendChild(paragraph);
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
     
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return messageDiv;
    }
   
    sendButton.addEventListener('click', sendMessage);
     
    userInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });
  
    clearButton.addEventListener('click', async () => {
        if (confirm('Are you sure you want to clear the chat history?')) {
            chatMessages.innerHTML = `
                <div class="message assistant">
                    <div class="message-content">
                        <p>Hello! I'm your Medical AI Assistant. How can I help you today?</p>
                    </div>
                </div>
            `;
 
            await fetch('/clear_history', { method: 'POST' });
        }
    });
  
    imageButton.addEventListener('click', () => {
        imageInput.click();
    });
    
    imageInput.addEventListener('change', (event) => {
        if (event.target.files.length > 0) {
            selectedImage = event.target.files[0];
            imageButton.innerHTML = '<i class="fas fa-check"></i>';
            imageButton.style.color = 'green';
        }
    });
 
    micButton.addEventListener('click', async () => {
        if (!isRecording) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];
                
                mediaRecorder.addEventListener('dataavailable', event => {
                    audioChunks.push(event.data);
                });
                
                mediaRecorder.addEventListener('stop', async () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                 
                    const recordingIndicator = document.createElement('div');
                    recordingIndicator.className = 'recording-indicator';
                    recordingIndicator.innerHTML = '<i class="fas fa-microphone"></i> Processing audio...';
                    userInput.parentNode.appendChild(recordingIndicator);
                  
                    const formData = new FormData();
                    formData.append('audio', audioBlob, 'recording.wav');
                    formData.append('message', '');
                    formData.append('tone', toneSelector.value);
                    
                    try {
                        const response = await fetch('/send_message', {
                            method: 'POST',
                            body: formData
                        });
                        
                        const data = await response.json();
                         
                        if (data.transcribed_text) {
                            userInput.value = data.transcribed_text;
                            addMessageToChat('user', data.transcribed_text);
                        }
                         
                        const aiMessage = addMessageToChat('assistant', data.ai_response);
                       
                        chatMessages.scrollTop = chatMessages.scrollHeight;
                        
                    } catch (error) {
                        console.error('Error:', error);
                    } finally {
                        recordingIndicator.remove();
                        micButton.innerHTML = '<i class="fas fa-microphone"></i>';
                        micButton.style.color = '';
                    }
                    
                    isRecording = false;
                });
                 
                mediaRecorder.start();
                isRecording = true;
                micButton.innerHTML = '<i class="fas fa-stop"></i>';
                micButton.style.color = 'red';
                 
                setTimeout(() => {
                    if (mediaRecorder && mediaRecorder.state === 'recording') {
                        mediaRecorder.stop();
                    }
                }, 15000);
                
            } catch (error) {
                console.error('Error accessing microphone:', error);
                alert('Unable to access microphone. Please check permissions.');
            }
        } else {
            mediaRecorder.stop();
            isRecording = false;
            micButton.innerHTML = '<i class="fas fa-microphone"></i>';
            micButton.style.color = '';
        }
    });
     
    const reminderForm = document.getElementById('reminder-form');
    const reminderStatus = document.getElementById('reminder-status');
    
    reminderForm.addEventListener('submit', async (event) => {
        event.preventDefault();
         
        const formData = new FormData(reminderForm);
         
        if (!formData.get('confirm')) {
            reminderStatus.textContent = '❌ Please check the confirmation box before submitting.';
            reminderStatus.className = 'status-message error';
            return;
        }
        
        try {
            const response = await fetch('/create_reminder', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                reminderStatus.textContent = data.message;
                reminderStatus.className = 'status-message success';
                reminderForm.reset();
            } else {
                reminderStatus.textContent = data.message;
                reminderStatus.className = 'status-message error';
            }
            
        } catch (error) {
            console.error('Error:', error);
            reminderStatus.textContent = '❌ An error occurred. Please try again.';
            reminderStatus.className = 'status-message error';
        }
    });
   
    const dateInput = document.getElementById('date');
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
        dateInput.value = `${yyyy}-${mm}-${dd}`;
    });