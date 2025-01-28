document.addEventListener('DOMContentLoaded', function () {
    const dailySummariesBody = document.getElementById("dailySummariesBody");
    const calendar = document.getElementById("calendar"); // The date input element
    const refreshButton = document.getElementById("refreshButton"); // Add this line to get the refresh button element
    
    let selectedDate = calendar.value || ''; // Initialize selectedDate with the current value of the calendar input or an empty string

    // Function to fetch and display daily summaries based on the selected date
    async function fetchDailySummaries(date = null) {
        try {
            let url = '/user_daily_summery/';
            if (date) {
                url = `/user_daily_summery/?date=${date}`; // If a date is selected, append it to the URL
            }

            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();

            // Populate the table with the fetched data
            dailySummariesBody.innerHTML = data.summaries.map(summary => `
                <tr>
                    <td>${summary.date}</td>
                    <td>${summary.bmr}</td>
                    <td>${summary.calories_in}</td>
                    <td>${summary.calories_out}</td>
                    <td>${summary.net_calories}</td>
                    <td>
                        <button class="btn btn-primary" onclick="viewDetails('${summary.date}')">View</button>
                    </td>
                </tr>
            `).join('');

            
        } catch (error) {
            console.error('Error fetching daily summaries:', error);
        }
    }

    // Set up initial state
    fetchDailySummaries(selectedDate);

    // Event listener for the calendar date change
    calendar.addEventListener('change', function () {
        selectedDate = calendar.value;  // Update selectedDate
        fetchDailySummaries(selectedDate); // Fetch summaries for the selected date
    });

    // Refresh button functionality
    if (refreshButton) {
        refreshButton.addEventListener("click", function () {
            fetchDailySummaries(selectedDate); // Re-fetch summaries with the current selected date
        });
    }

    // Function to view details for a specific date
    window.viewDetails = function (date) {
        // Redirect to the detailed page with the selected date
        window.location.href = `/user_daily_logs_dashboard/?date=${date}`;
    };
});
