document.addEventListener('DOMContentLoaded', function() {
    const taskForm = document.getElementById('taskForm');
    const tasksList = document.getElementById('tasksList');

    // Load initial tasks
    loadTasks();

    // Handle form submission
    taskForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = {
            title: document.getElementById('title').value,
            description: document.getElementById('description').value,
            assigned_to: document.getElementById('assigned_to').value,
            due_date: document.getElementById('due_date').value
        };

        try {
            const response = await fetch('/api/tasks', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error('Failed to create task');
            }

            taskForm.reset();
            loadTasks();
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to create task');
        }
    });

    // Load tasks from server
    async function loadTasks() {
        try {
            const response = await fetch('/api/tasks');
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const tasks = await response.json();

            // Render tasks
            tasksList.innerHTML = tasks.map(task => `
                <div class="card mb-3">
                    <div class="card-body">
                        <h5 class="card-title">${task.title}</h5>
                        <p class="card-text">${task.description || 'No description provided'}</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">Assigned to: ${task.assigned_to}</small>
                            <div class="btn-group">
                                <button class="btn btn-sm btn-success task-status-btn" 
                                        data-task-id="${task.id}" 
                                        data-status="completed"
                                        ${task.status === 'completed' ? 'disabled' : ''}>
                                    Complete
                                </button>
                            </div>
                        </div>
                        ${task.due_date ? `
                        <div class="mt-2">
                            <small class="text-muted">Due: ${new Date(task.due_date).toLocaleString()}</small>
                        </div>
                        ` : ''}
                    </div>
                </div>
            `).join('') || '<p class="text-muted">No tasks found</p>';

            // Add event listeners to new task status buttons
            document.querySelectorAll('.task-status-btn').forEach(btn => {
                btn.addEventListener('click', handleStatusUpdate);
            });
        } catch (error) {
            console.error('Error loading tasks:', error);
            tasksList.innerHTML = '<p class="text-danger">Failed to load tasks</p>';
            alert('Failed to fetch tasks. Please try again later.');
        }
    }

    // Handle task status updates
    async function handleStatusUpdate(e) {
        const taskId = e.target.dataset.taskId;
        const newStatus = e.target.dataset.status;

        try {
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ status: newStatus })
            });

            if (!response.ok) {
                throw new Error('Failed to update task status');
            }

            loadTasks();
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to update task status');
        }
    }
});