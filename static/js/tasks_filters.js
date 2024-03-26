document.addEventListener("DOMContentLoaded", function () {
    var statusCheckboxes = document.querySelectorAll('.status-checkbox');
    var statusAllCheckbox = document.getElementById('status_all');
    var priorityCheckboxes = document.querySelectorAll('.priority-checkbox');
    var priorityAllCheckbox = document.getElementById('priority_all');

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
});