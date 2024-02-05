const { createApp } = Vue;

const TaskApp = {
    data() {
        return {
            task: {'title': ''},
            tasks: [],
            message: "Hello, ",
            user_name: 'Maria',
            today_date: 'Today is 12 Jan'
        };
    },
    async created() {
        await this.getTasks();
    },
    methods: {
        async getTasks() {
            const response = await fetch(window.location, {
                method: 'get',
                headers: {'X-Requested-With': 'XMLHttpRequest'}
            });
            this.tasks = await response.json();
        },
        async createTask() {
            const response = await fetch(window.location + 'create', {
                method: 'post',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(this.task)
            });
            await this.getTasks(); // Refresh tasks after creating
        }
    },
    delimiters: ['[[', ']]']  // Change delimiters to avoid conflicts
};

createApp(TaskApp).mount("#app");
