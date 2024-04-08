console.log("JavaScript file loaded.");

if (typeof Vue !== 'undefined') {
    console.log("Vue is loaded, initializing app.");

    const app = Vue.createApp({
        data() {
            return {
                task: { 'title': '' },
                tasks: [],
                message: "Hello, ",
                user_name: 'Maria',
                today_date: 'Today is 12 Jan',
                submitted: false,
                chosenDay: '',
            };
        },
        async created() {
            await this.getTasks();
        },
        methods: {
            async getTasks() {
                const response = await fetch(window.location, {
                    method: 'GET',
                    headers: { 'X-Requested-With': 'XMLHttpRequest' },
                });
                this.tasks = await response.json();
            },
            async createTask() {
                const response = await fetch(window.location + 'create', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: JSON.stringify(this.task),
                });
                await this.getTasks();
            },
            async submitChoice() {
                 console.log("Button 'Submit Choice' clicked."); // Log when the button is clicked
    console.log("Chosen day:", this.chosenDay); // Log the chosen day

                const response = await fetch('/choose', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: JSON.stringify({ choice: this.chosenDay }),
                });
                const data = await response.json();
                 console.log("Server response:", data);
                if (data.success) {
                console.log("Choice submitted successfully.");
                    this.submitted = true;
                } else {
                 console.error("Failed to submit choice. Error:", data.error);
                    this.submitted = false;
                    console.error("Failed to submit choice:", data.error);
                }
            }
        }
    }).mount("#app");
} else {
    console.error("Vue is not defined.");
}



// Utility Functions
function updateTime() {
    const now = new Date();
    const dateOptions = {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        timeZone: "Europe/Amsterdam",
    };
    const timeOptions = {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
        timeZone: "Europe/Amsterdam",
    };
    const dateDisplay = document.getElementById("dateDisplay");
    const timeDisplay = document.getElementById("timeDisplay");
    const formattedDate = now.toLocaleDateString("en-US", dateOptions);
    const formattedTime = now.toLocaleTimeString("en-US", timeOptions);
    dateDisplay.innerHTML = formattedDate;
    timeDisplay.innerHTML = formattedTime;
}

function fetchMessages() {
    const csrf_token = document.querySelector('input[name="csrf_token"]').value; // Assuming you have an input field for CSRF token

    fetch('/get-messages', {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrf_token, // Make sure this token is correctly obtained from your HTML
            'Content-Type': 'application/json'
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        const messagesDiv = document.getElementById('messages');
        messagesDiv.innerHTML = ''; // Clear previous messages
        data.forEach(msg => {
            const p = document.createElement('p');
            p.textContent = msg;
            messagesDiv.appendChild(p);
        });
    })
    .catch(error => console.error('Error:', error));
}



// Event Listeners and DOM Manipulation
document.getElementById('addGroceryForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission
    console.log("Form submit event triggered.");
    const formData = new FormData(this); // 'this' refers to the form itself
    fetch('/create', {
        method: 'POST',
        body: formData, // Sending the form data as FormData
    }).then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log("Product added successfully.");
            // Insert the new item at the top of the list
            const groceriesList = document.querySelector('#groceriesList');
            const newItem = document.createElement('div');
            newItem.classList.add('card', 'mb-3');
            newItem.setAttribute('data-product-id', data.product.id);
            newItem.innerHTML = `
                <div class="card-body row justify-content-between px-4">
                    <div>${data.product.title}</div>
                    ${data.product.completed ? '' : `<input type="checkbox" class="form-check-input" onchange="updateProductStatus(this, ${data.product.id})">`}
                </div>
            `;
            groceriesList.insertBefore(newItem, groceriesList.firstChild);
            document.getElementById('addGroceryForm').reset();
        } else {
            alert('Error adding product');
        }
    }).catch(error => console.error('Error:', error));
});


function updateProductStatus(checkbox, productId) {
    const isChecked = checkbox.checked;
    fetch(`/update/${productId}`, {
        method: 'POST',
        body: JSON.stringify({ completed: isChecked }),
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        const productCard = checkbox.closest('.card.mb-3');
        if (data.completed) {
            const groceriesList = document.querySelector('#groceriesList');
            groceriesList.appendChild(productCard); // Move to bottom
            checkbox.style.display = 'none'; // Hide checkbox
            productCard.classList.add('strikethrough'); // Add class to indicate completion
        } else {
            checkbox.style.display = 'block'; // Ensure checkbox is visible if item is un-checked
            productCard.classList.remove('strikethrough'); // Remove strikethrough if item is un-checked
        }
    })
    .catch(error => console.error('Error:', error));
}

// Repeated actions
setInterval(fetchMessages, 105000); // это надо в messages.html
setInterval(updateTime, 1000);
