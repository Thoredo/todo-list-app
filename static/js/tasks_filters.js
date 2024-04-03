document.addEventListener("DOMContentLoaded", function () {
    var statusAllCheckbox = document.getElementById('status_all');
    var priorityAllCheckbox = document.getElementById('priority_all');
    var statusCheckboxes = document.querySelectorAll('.status-checkbox');
    var priorityCheckboxes = document.querySelectorAll('.priority-checkbox');

    if (localStorage.getItem('statusAllCheckboxChecked')) {
        statusAllCheckbox.checked = JSON.parse(localStorage.getItem('statusAllCheckboxChecked'));
    }
    if (localStorage.getItem('priorityAllCheckboxChecked')) {
        priorityAllCheckbox.checked = JSON.parse(localStorage.getItem('priorityAllCheckboxChecked'));
    }

    // Retrieve checkbox state from localStorage if available
    var checkedStatusCheckboxes = localStorage.getItem('checkedStatusCheckboxes') ? JSON.parse(localStorage.getItem('checkedStatusCheckboxes')) : null;
    var checkedPriorityCheckboxes = localStorage.getItem('checkedPriorityCheckboxes') ? JSON.parse(localStorage.getItem('checkedPriorityCheckboxes')) : null;

    // Restore checkbox states if available
    if (checkedStatusCheckboxes && checkedStatusCheckboxes.length === statusCheckboxes.length) {
        statusCheckboxes.forEach(function (checkbox, index) {
            checkbox.checked = checkedStatusCheckboxes[index];
        });
    }
    if (checkedPriorityCheckboxes && checkedPriorityCheckboxes.length === priorityCheckboxes.length) {
        priorityCheckboxes.forEach(function (checkbox, index) {
            checkbox.checked = checkedPriorityCheckboxes[index];
        });
    }



    statusCheckboxes.forEach(function (checkbox) {
        checkbox.addEventListener('change', function () {
            if (statusAllCheckbox.checked && this !== statusAllCheckbox) {
                statusAllCheckbox.checked = false;
            }
            updateTasks();
        });
    });

    statusAllCheckbox.addEventListener('change', function () {
        if (this.checked) {
            statusCheckboxes.forEach(function (checkbox) {
                if (checkbox !== statusAllCheckbox) {
                    checkbox.checked = false;
                }
            });
        }
        updateTasks();
    });

    priorityCheckboxes.forEach(function (checkbox) {
        checkbox.addEventListener('change', function () {
            if (priorityAllCheckbox.checked && this !== priorityAllCheckbox) {
                priorityAllCheckbox.checked = false;
            }
            updateTasks();
        });
    });

    priorityAllCheckbox.addEventListener('change', function () {
        if (this.checked) {
            priorityCheckboxes.forEach(function (checkbox) {
                if (checkbox !== priorityAllCheckbox) {
                    checkbox.checked = false;
                }
            });
        }
        updateTasks();
    });


    function updateTasks() {
        localStorage.setItem('statusAllCheckboxChecked', statusAllCheckbox.checked);
        localStorage.setItem('priorityAllCheckboxChecked', priorityAllCheckbox.checked);
        localStorage.setItem('checkedStatusCheckboxes', JSON.stringify(Array.from(statusCheckboxes).map(function (checkbox) {
            return checkbox.checked;
        })));
        localStorage.setItem('checkedPriorityCheckboxes', JSON.stringify(Array.from(priorityCheckboxes).map(function (checkbox) {
            return checkbox.checked;
        })));

        var selectedStatuses = [];
        statusCheckboxes.forEach(function (checkbox) {
            if (checkbox.checked) {
                selectedStatuses.push(checkbox.value);
            }
        });

        var selectedPriorities = [];
        priorityCheckboxes.forEach(function (checkbox) {
            if (checkbox.checked) {
                selectedPriorities.push(checkbox.value);
            }
        });


        var tasks = document.querySelectorAll('.task-row');
        tasks.forEach(function (task) {
            var status = task.dataset.status;
            var priority = task.dataset.priority;
            if ((selectedStatuses.includes(status) || selectedStatuses.includes('all_tasks')) &&
                (selectedPriorities.includes(priority) || selectedPriorities.includes('all_priorities'))) {
                task.style.display = 'table-row';
            } else if (selectedStatuses.includes('in_progress') && (status === 'due_today' || status === 'overdue') &&
                (selectedPriorities.includes(priority) || selectedPriorities.includes('all_priorities'))) {
                task.style.display = 'table-row';
            } else {
                task.style.display = 'none';
            }
        });
    }
    console.log(statusCheckboxes)
    updateTasks();
});