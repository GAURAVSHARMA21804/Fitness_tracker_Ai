// Modal Functionality
const addDataBtn = document.getElementById('addDataBtn');
const addDataModal = document.getElementById('addDataModal');
const closeModalBtn = document.getElementById('closeModalBtn');
const cancelBtn = document.getElementById('cancelBtn');

addDataBtn.addEventListener('click', () => {
    addDataModal.style.display = 'flex';
});

closeModalBtn.addEventListener('click', () => {
    addDataModal.style.display = 'none';
});

cancelBtn.addEventListener('click', () => {
    addDataModal.style.display = 'none';
});

// Tab Switching
const foodTab = document.getElementById('foodTab');
const activityTab = document.getElementById('activityTab');
const addFoodForm = document.getElementById('addFoodForm');
const addActivityForm = document.getElementById('addActivityForm');

foodTab.addEventListener('click', () => {
    foodTab.classList.add('active');
    activityTab.classList.remove('active');
    addFoodForm.classList.add('active');
    addActivityForm.classList.remove('active');
});

activityTab.addEventListener('click', () => {
    activityTab.classList.add('active');
    foodTab.classList.remove('active');
    addActivityForm.classList.add('active');
    addFoodForm.classList.remove('active');
});

// // JavaScript logic for handling form submission
// document.getElementById('saveBtn').addEventListener('click', function(event) {
//     event.preventDefault(); // Prevent the default form submission behavior

//     // Check which tab is active and submit the corresponding form
//     if (document.getElementById('foodTab').classList.contains('active')) {
//         submitFoodForm();
//     } else if (document.getElementById('activityTab').classList.contains('active')) {
//         submitActivityForm();
//     }


// });

document.addEventListener('DOMContentLoaded', function() {
    // Common elements
    const saveBtn = document.getElementById('saveBtn');
    const foodSearchInput = document.getElementById('foodSearch');
    const foodList = document.getElementById('foodList');
    const selectedFoodId = document.getElementById('selectedFoodId');
    const foodGroup = document.getElementById('foodGroup');
    const mealTypeInput = document.getElementById('mealType');
    const servingInput = document.getElementById('serving');
    const activitySearchInput = document.getElementById('activitySearch');
    const activityList = document.getElementById('activityList');
    const selectedActivityId = document.getElementById('selectedActivityId');
    const specificMotion = document.getElementById('specificMotion');
    const metValue = document.getElementById('metValue');
    const duration = document.getElementById('duration');
    const activityDescriptionInput = document.getElementById('activityDescription');
    

    
    // Function to get CSRF token (for AJAX requests)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Handle tab-based form submission
    saveBtn.addEventListener('click', function(event) {
        event.preventDefault();
        if (document.getElementById('foodTab').classList.contains('active')) {
            submitFoodForm();
        } else {
            submitActivityForm();
        }
    });

    // Handle food search with debouncing
    let debounceTimeout;
    foodSearchInput.addEventListener('input', function() {
        const query = foodSearchInput.value.trim();
        clearTimeout(debounceTimeout);

        if (query.length > 0) {
            debounceTimeout = setTimeout(() => {
                fetch(`/search_food/?query=${query}`)
                    .then(response => response.json())
                    .then(data => {
                        foodList.innerHTML = '';  // Clear previous results
                        if (data.foods.length > 0) {
                            data.foods.forEach(food => {
                                const li = document.createElement('li');
                                li.textContent = food.food_name;
                                li.dataset.foodId = food.food_id;
                                li.dataset.foodGroup = food.food_group;

                                li.addEventListener('click', function() {
                                    foodSearchInput.value = food.food_name;
                                    foodGroup.value = food.food_group;
                                    selectedFoodId.value = food.food_id;
                                    foodList.style.display = 'none';  // Hide list after selection
                                });

                                foodList.appendChild(li);
                            });
                            foodList.style.display = 'block';  // Show results
                        } else {
                            const li = document.createElement('li');
                            li.textContent = 'No results found';
                            li.classList.add('no-results');
                            foodList.appendChild(li);
                            foodList.style.display = 'block';
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching food data:', error);
                        foodList.style.display = 'none';  // Hide list on error
                    });
            }, 500);  // Wait 500ms after user stops typing
        } else {
            foodList.style.display = 'none';  // Hide list if input is empty
        }
    });

    // Handle activity search with debouncing
    activitySearchInput.addEventListener('input', function() {
        const query = activitySearchInput.value.trim();
        if (query.length > 2) {
            fetch(`/search_activity/?query=${query}`)
                .then(response => response.json())
                .then(data => {
                    activityList.innerHTML = '';  // Clear previous results
                    if (data.activities.length > 0) {
                        data.activities.forEach(activity => {
                            const li = document.createElement('li');
                            li.textContent = `${activity.activity_name} - ${activity.specific_motion} (${activity.mets} METs)`;
                            li.setAttribute('data-id', activity.activity_id);

                            li.addEventListener('click', function() {
                                selectedActivityId.value = activity.activity_id;
                                activitySearchInput.value = activity.activity_name;
                                specificMotion.value = activity.specific_motion;
                                metValue.value = activity.mets;
                                activityList.innerHTML = '';  // Clear list
                                activityList.style.display = 'none';  // Hide list
                            });

                            activityList.appendChild(li);
                        });
                    } else {
                        const noResult = document.createElement('li');
                        noResult.textContent = 'No results found';
                        noResult.classList.add('no-results');
                        activityList.appendChild(noResult);
                    }
                    activityList.style.display = 'block';  // Show results
                });
        } else {
            activityList.innerHTML = '';
            activityList.style.display = 'none';  // Hide list if query is short
        }
    });

    // Handle form submission for food log
    function submitFoodForm() {
        const foodDate = document.getElementById('foodDate').value;
        const foodId = selectedFoodId.value;
        const mealType = mealTypeInput.value;
        const servingCount = servingInput.value;

        fetch('/save_food_log/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                date: foodDate,
                food_item: foodId,
                meal_type: mealType,
                serving_count: servingCount,
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showSuccessMessage(data.message);
                resetForm('food');
            } else {
                alert(data.error);
            }
        })
        .catch(error => console.error('Error:', error));
    }

    // Handle form submission for activity log
    function submitActivityForm() {
        const activityDate = document.getElementById('activityDate').value;
        const activityId = selectedActivityId.value;
        const durationMinutes = duration.value;
        const description = activityDescriptionInput.value;

        fetch('/save_activity_log/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                date: activityDate,
                activity_id: activityId,
                duration_minutes: durationMinutes,
                description: description,
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showSuccessMessage(data.message);
                resetForm('activity');
            } else {
                alert(data.error);
            }
        })
        .catch(error => console.error('Error:', error));
    }

    // Reset form after submission
    function resetForm(type) {
        if (type === 'food') {
            document.getElementById('addFoodForm').reset();
            foodList.innerHTML = '';
            foodGroup.value = '';
            mealTypeInput.value = '';
            servingInput.value = '';
            selectedFoodId.value = '';
        } else if (type === 'activity') {
            document.getElementById('addActivityForm').reset();
            activityList.innerHTML = '';
            selectedActivityId.value = '';
            activityDescriptionInput.value = '';
            duration.value = '';
            specificMotion.value = '';
            metValue.value = '';
        }
    }

    // Display success message
    function showSuccessMessage(message) {
        const successBox = document.createElement('div');
        successBox.classList.add('success-message');
        successBox.textContent = message;
        document.body.appendChild(successBox);

        setTimeout(() => {
            successBox.style.display = 'none';
        }, 3000);
    }
   
        
});

