document.addEventListener("DOMContentLoaded", function () {
    var checkboxes = document.querySelectorAll('.status-checkbox');
    var allCheckbox = document.getElementById('status_all');

    checkboxes.forEach(function (checkbox) {
        checkbox.addEventListener('change', function () {
            if (allCheckbox.checked && this !== allCheckbox) {
                allCheckbox.checked = false;
            }
            updateTasks();
        });
    });

    allCheckbox.addEventListener('change', function () {
        if (this.checked) {
            checkboxes.forEach(function (checkbox) {
                if (checkbox !== allCheckbox) {
                    checkbox.checked = false;
                }
            });
        }
        updateTasks();
    });


    function updateTasks() {
        var selectedStatuses = [];
        checkboxes.forEach(function (checkbox) {
            if (checkbox.checked) {
                selectedStatuses.push(checkbox.value);
            }
        });


        var tasks = document.querySelectorAll('.task-row');
        tasks.forEach(function (task) {
            var status = task.dataset.status;
            if (selectedStatuses.includes(status) || selectedStatuses.includes('all_tasks')) {
                task.style.display = 'table-row';
            } else {
                task.style.display = 'none';
            }
        });
    }
});