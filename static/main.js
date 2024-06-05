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
            'X-CSRFToken': csrf_token,
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

document.addEventListener("DOMContentLoaded", function() {
    const addGroceryForm = document.getElementById('addGroceryForm');
    addGroceryForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        const titleInput = addGroceryForm.querySelector('.form-control');
        const title = titleInput.value.trim();

        if (title) {
            const response = await fetch('/add_grocery', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ title })
            });

            if (response.ok) {
    const result = await response.json();
    if (result.success) {
        const product = result.item;
        const groceriesList = document.getElementById('groceriesList');
        const card = document.createElement('div');
        card.className = 'card';
        card.setAttribute('data-product-id', product.id);
        card.innerHTML = `
            <div class="card-body row justify-content-between px-2">
                <div class="grocery-item">
                    <input type="checkbox" class="form-check-input" onchange="updateProductStatus(this, ${product.id}, 'grocery')">
                    <div>${product.title}</div>
                </div>
            </div>
        `;
        groceriesList.insertBefore(card, groceriesList.firstChild);  // Insert at the top
        titleInput.value = '';
    } else {
        console.error('Failed to add grocery item:', result.error);
    }
} else {
    console.error('Failed to add grocery item:', response.statusText);
}

        }
    });

    const addTaskForm = document.getElementById('addTaskForm');
    addTaskForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        const titleInput = addTaskForm.querySelector('.form-control');
        const title = titleInput.value.trim();

        if (title) {
            const response = await fetch('/add_task', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ title })
            });

            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    const task = result.item;
                    const tasksList = document.getElementById('tasksList');
                    const card = document.createElement('div');
                    card.className = 'card';
                    card.setAttribute('data-task-id', task.id);
                    card.innerHTML = `
                        <div class="card-body row justify-content-between px-2">
                            <div class="task-item">
                                <input type="checkbox" class="form-check-input" onchange="updateProductStatus(this, ${task.id}, 'task')">
                                <div>${task.title}</div>
                            </div>
                        </div>
                    `;
                    tasksList.appendChild(card);
                    titleInput.value = '';
                } else {
                    console.error('Failed to add task:', result.error);
                }
            } else {
                console.error('Failed to add task:', response.statusText);
            }
        }

    });
});

async function updateProductStatus(checkbox, id, type) {
    const completed = checkbox.checked;
    const response = await fetch('/update_status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id, completed, type })
    });

    if (response.ok) {
        const result = await response.json();
        if (result.success) {
            const item = checkbox.closest('.card');
            item.querySelector('div').classList.toggle('strikethrough', completed);

            const parentList = item.parentNode;
            parentList.removeChild(item);
            parentList.appendChild(item);  // Append item to move it to the bottom
        } else {
            console.error('Failed to update status:', result.error);
        }
    } else {
        console.error('Failed to update status:', response.statusText);
    }
}



// Repeated actions
// setInterval(fetchMessages, 105000); // это надо в messages.html
setInterval(updateTime, 1000);
