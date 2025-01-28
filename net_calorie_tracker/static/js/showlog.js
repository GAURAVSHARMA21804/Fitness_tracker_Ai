document.addEventListener('DOMContentLoaded', function () {
    const calendar = document.getElementById("calendar");
    const refreshButton = document.getElementById("refreshButton");
    const foodLogsBody = document.getElementById("foodLogsBody");
    const activityLogsBody = document.getElementById("activityLogsBody");
    const selectedDateDisplay = document.getElementById("selected-date-display");

    // Get the selected date from the URL parameter
    const urlParams = new URLSearchParams(window.location.search);
    let selectedDate = urlParams.get('date') || new Date().toISOString().split("T")[0]; // Default to today's date if no date parameter is present

    // Function to fetch logs for the given date
    async function fetchLogs(date) {
        try {
            const response = await fetch(`/get-logs/?date=${date}`);
            const data = await response.json();
            console.log("Fetched data:", data); // Check the structure of the data

            // Update food logs
            foodLogsBody.innerHTML = data.food_logs.map(log => `
                <tr id="food_log_${log.id}">
                    <td>${log.date}</td>
                    <td>${log.food_name}</td>
                    <td>${log.meal_type}</td>
                    <td>${log.food_group}</td>
                    <td>${log.serving_count}</td>
                    <td>${log.total_calories}</td>
                    <td>
                        <button class="btn btn-delete" onclick="deleteFoodLog(${log.id})">Delete</button>
                    </td>
                </tr>
            `).join("");

            // Update activity logs
            activityLogsBody.innerHTML = data.activity_logs.map(log => `
                <tr id="activity_log_${log.id}">
                    <td>${log.date}</td>
                    <td>${log.activity_name}</td>
                    <td>${log.description || "N/A"}</td>
                    <td>${log.duration_minutes} mins</td>
                    <td>${log.calories_burned}</td>
                    <td>
                        <button class="btn btn-delete" onclick="deleteActivityLog(${log.id})">Delete</button>
                    </td>
                </tr>
            `).join("");

            // Update summary
            document.getElementById('bmrValue').textContent = data.summary.bmr || '-';
            document.getElementById('caloriesInValue').textContent = data.summary.calories_in || '-';
            document.getElementById('caloriesOutValue').textContent = data.summary.calories_out || '-';
            document.getElementById('netCaloriesValue').textContent = data.summary.net_calories || '-';

        } catch (error) {
            console.error("Error fetching logs:", error);
        }
    }

    // Set up initial state
    selectedDateDisplay.textContent = `Date: ${selectedDate}`;
    fetchLogs(selectedDate);

    // Update logs on date change
    calendar.addEventListener("change", function () {
        selectedDate = calendar.value;
        selectedDateDisplay.textContent = `Date: ${selectedDate}`;
        fetchLogs(selectedDate);
    });

    // Refresh button functionality
    refreshButton.addEventListener("click", function () {
        fetchLogs(selectedDate);
    });

    // Delete Food Log
    window.deleteFoodLog = function (logId) {
        if (confirm("Are you sure you want to delete this food log?")) {
            fetch(`/api/delete_food_log/${logId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value, // CSRF token
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    alert(data.message); // Show success message
                    document.getElementById(`food_log_${logId}`).remove(); // Remove the row from the table
                } else if (data.error) {
                    alert(data.error); // Show error message
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    };

    // Delete Activity Log
    window.deleteActivityLog = function (logId) {
        if (confirm("Are you sure you want to delete this activity log?")) {
            fetch(`/api/delete_activity_log/${logId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value, // CSRF token
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    alert(data.message); // Show success message
                    document.getElementById(`activity_log_${logId}`).remove(); // Remove the row from the table
                } else if (data.error) {
                    alert(data.error); // Show error message
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    };
});
