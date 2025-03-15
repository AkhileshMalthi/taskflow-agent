document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const tasksList = document.getElementById('tasksList');
    const tasksFilter = document.getElementById('tasksFilter');
    const taskForm = document.getElementById('taskForm');
    
    // App State
    let currentTasks = [];
    let currentFilter = 'all';
    
    // Initialize
    initializeApp();
    
    function initializeApp() {
        fetchTasks();
        setupEventListeners();
    }
    
    function setupEventListeners() {
        if (taskForm) {
            taskForm.addEventListener('submit', handleTaskFormSubmit);
        }
        
        if (tasksFilter) {
            tasksFilter.addEventListener('change', handleFilterChange);
        }
    }
    
    function fetchTasks() {
        fetch('/api/tasks')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                currentTasks = data;
                renderTasks();
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
                alert('Failed to fetch tasks. Please try again later.');
                if (tasksList) {
                    tasksList.innerHTML = '<div class="alert alert-danger">Failed to load tasks</div>';
                }
            });
    }
    
    function renderTasks() {
        if (!tasksList) return;
        
        const filteredTasks = filterTasks(currentTasks);
        
        if (filteredTasks.length === 0) {
            tasksList.innerHTML = '<div class="alert alert-info">No tasks found</div>';
            return;
        }
        
        tasksList.innerHTML = filteredTasks.map(task => createTaskCard(task)).join('');
        
        // Add event listeners to task actions
        document.querySelectorAll('.task-complete-btn').forEach(btn => {
            btn.addEventListener('click', handleCompleteTask);
        });
        
        document.querySelectorAll('.task-delete-btn').forEach(btn => {
            btn.addEventListener('click', handleDeleteTask);
        });
    }
    
    function createTaskCard(task) {
        const dueDate = task.due_date ? new Date(task.due_date) : null;
        const isOverdue = dueDate && dueDate < new Date() && task.status !== 'completed';
        
        return `
        <div class="card mb-3 ${isOverdue ? 'border-danger' : ''}">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="card-title mb-0 ${task.status === 'completed' ? 'text-muted text-decoration-line-through' : ''}">${task.title}</h5>
                <span class="badge ${getStatusBadgeClass(task.status)}">${task.status}</span>
            </div>
            <div class="card-body">
                <p class="card-text">${task.description || 'No description provided'}</p>
                <div class="d-flex justify-content-between align-items-center">
                    <small class="text-muted">Assigned to: ${task.assigned_to}</small>
                    ${dueDate ? `
                    <small class="${isOverdue ? 'text-danger' : 'text-muted'}">
                        Due: ${dueDate.toLocaleString()}
                    </small>
                    ` : ''}
                </div>
            </div>
            <div class="card-footer d-flex justify-content-end">
                <button class="btn btn-sm btn-success me-2 task-complete-btn" 
                        data-task-id="${task.id}" 
                        ${task.status === 'completed' ? 'disabled' : ''}>
                    Mark Complete
                </button>
                <button class="btn btn-sm btn-danger task-delete-btn" 
                        data-task-id="${task.id}">
                    Delete
                </button>
            </div>
        </div>
        `;
    }
    
    function getStatusBadgeClass(status) {
        switch(status) {
            case 'completed': return 'bg-success';
            case 'in_progress': return 'bg-primary';
            case 'pending': return 'bg-warning';
            default: return 'bg-secondary';
        }
    }
    
    function filterTasks(tasks) {
        switch(currentFilter) {
            case 'completed':
                return tasks.filter(task => task.status === 'completed');
            case 'pending':
                return tasks.filter(task => task.status === 'pending');
            case 'in_progress':
                return tasks.filter(task => task.status === 'in_progress');
            case 'all':
            default:
                return tasks;
        }
    }
    
    function handleFilterChange(e) {
        currentFilter = e.target.value;
        renderTasks();
    }
    
    function handleTaskFormSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const taskData = {
            title: formData.get('title'),
            description: formData.get('description'),
            assigned_to: formData.get('assigned_to'),
            due_date: formData.get('due_date')
        };
        
        fetch('/api/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(taskData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to create task');
            }
            return response.json();
        })
        .then(() => {
            e.target.reset();
            fetchTasks();
        })
        .catch(error => {
            console.error('Error creating task:', error);
            alert('Failed to create task. Please try again.');
        });
    }
    
    function handleCompleteTask(e) {
        const taskId = e.target.dataset.taskId;
        
        fetch(`/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: 'completed' })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to update task');
            }
            fetchTasks();
        })
        .catch(error => {
            console.error('Error updating task:', error);
            alert('Failed to update task. Please try again.');
        });
    }
    
    function handleDeleteTask(e) {
        if (!confirm('Are you sure you want to delete this task?')) {
            return;
        }
        
        const taskId = e.target.dataset.taskId;
        
        fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to delete task');
            }
            fetchTasks();
        })
        .catch(error => {
            console.error('Error deleting task:', error);
            alert('Failed to delete task. Please try again.');
        });
    }
});
