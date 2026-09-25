// Wait for the HTML elements to load before attaching events
document.addEventListener('DOMContentLoaded', function() { 
    document.getElementById('add-todo-button').addEventListener('click', addTodo); 
}); 

function addTodo() { 
    var newTodo = document.getElementById('new-todo').value; 
    if (newTodo === '') { 
        alert('Please enter a todo'); 
        return; 
    } 
    var todoList = document.getElementById('todo-list'); 
    var li = document.createElement('li'); 
    // Create a new span to hold the task text
    var taskSpan = document.createElement('span');
    taskSpan.textContent = newTodo;
    li.appendChild(taskSpan);
    // Get current time
    var currentTime = new Date();
    var timeString = currentTime.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    var timeSpan = document.createElement('span');
    timeSpan.textContent = ' (' + timeString + ')';
    timeSpan.style.marginLeft = '10px';
    timeSpan.style.fontStyle = 'italic';
    li.appendChild(timeSpan);
    var deleteBtn = document.createElement('button'); 
    deleteBtn.textContent = 'Delete'; 
    deleteBtn.style.marginLeft = '10px';
    deleteBtn.onclick = function() { 
        todoList.removeChild(deleteBtn.parentElement); 
    }; 
    li.appendChild(deleteBtn); 
    todoList.appendChild(li); 
    document.getElementById('new-todo').value = ''; 
}