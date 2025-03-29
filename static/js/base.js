    // Add Todo JS
    console.log('base.js loaded');  // This will show if the file is loaded

    const todoForm = document.getElementById('todoForm');
    console.log('Found todo form:', todoForm); // This will show if we found the form

    if (todoForm) {
        console.log('Adding submit listener to todo form');
        todoForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            console.log('Form submitted - starting handler');

            try {
                const form = event.target;
                const formData = new FormData(form);
                const title = formData.get('title');
                const description = formData.get('description');
                const priority = formData.get('priority');

                console.log('Form data:', { title, description, priority });

                if (!title || title.length < 3 || title.length > 100) {
                    alert('Title must be between 3 and 100 characters');
                    return;
                }

                if (!description || description.length < 3 || description.length > 100) {
                    alert('Description must be between 3 and 100 characters');
                    return;
                }

                const payload = {
                    title: title.trim(),
                    description: description.trim(),
                    priority: parseInt(priority),
                    complete: false
                };

                console.log('About to send fetch request');
                
                // Get the token first
                const token = getCookie('access_token');
                if (!token) {
                    console.log('No token found');
                    alert('Please log in again.');
                    window.location.href = '/auth/login-page';
                    return;
                }

                console.log('Token found, sending request');
                
                // Make the fetch request
                const response = await fetch('/todos/todo', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(payload)
                });

                console.log('Response status:', response.status);

                if (response.ok) {
                    console.log('Todo created successfully');
                    const successAlert = document.getElementById('successAlert');
                    successAlert.textContent = 'Todo created successfully!';
                    successAlert.style.display = 'block';
                    form.reset();
                    alert('Todo created successfully!');
                    
                    // Hide the message after 3 seconds
                    setTimeout(() => {
                        successAlert.style.display = 'none';
                    }, 3000);
                    return;
                } else {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Failed to create todo');
                }
            } catch (error) {
                console.error('Error in form submission:', error);
                alert('Error: ' + error.message);
            }
        });
    }

    // Edit Todo JS
    const editTodoForm = document.getElementById('editTodoForm');
    if (editTodoForm) {
        editTodoForm.addEventListener('submit', async function (event) {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        var url = window.location.pathname;
        const todoId = url.substring(url.lastIndexOf('/') + 1);

        const payload = {
            title: data.title,
            description: data.description,
            priority: parseInt(data.priority),
            complete: data.complete === "on"
        };

        try {
            const token = getCookie('access_token');
            console.log(token)
            if (!token) {
                throw new Error('Authentication token not found');
            }

            console.log(`${todoId}`)

            const response = await fetch(`/todos/todo/${todoId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                window.location.href = '/todos/todo-page'; // Redirect to the todo page
            } else {
                // Handle error
                const errorData = await response.json();
                alert(`Error: ${errorData.detail}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        }
    });

        document.getElementById('deleteButton').addEventListener('click', async function () {
            var url = window.location.pathname;
            const todoId = url.substring(url.lastIndexOf('/') + 1);

            try {
                const token = getCookie('access_token');
                if (!token) {
                    throw new Error('Authentication token not found');
                }

                const response = await fetch(`/todos/todo/${todoId}`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    // Handle success
                    window.location.href = '/todos/todo-page'; // Redirect to the todo page
                } else {
                    // Handle error
                    const errorData = await response.json();
                    alert(`Error: ${errorData.detail}`);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            }
        });

        
    }

    // Login JS
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        console.log('Login form found');
        loginForm.addEventListener('submit', async function (event) {
            event.preventDefault();
            console.log('Login form submitted');

            const formData = new FormData(this);
            const payload = new URLSearchParams();
            payload.append('username', formData.get('username'));
            payload.append('password', formData.get('password'));
            payload.append('grant_type', 'password');

            try {
                console.log('Sending login request');
                const response = await fetch('/auth/token', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: payload.toString()
                });

                console.log('Response received:', response.status);

                if (!response.ok) {
                    const errorData = await response.json();
                    console.error('Login failed:', errorData.detail);
                    alert(errorData.detail || 'Login failed. Please check your credentials.');
                    return;
                }

                const data = await response.json();
                console.log('Login successful');
                // Set the token cookie
                document.cookie = `access_token=${data.access_token}; path=/`;
                // Redirect to todos page
                window.location.href = '/todos/todo-page';
            } catch (error) {
                console.error('Login error:', error);
                alert('An error occurred during login. Please try again.');
            }
        });
    }

    // Register JS
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async function (event) {
            event.preventDefault();

            const form = event.target;
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            if (data.password !== data.password2) {
                alert("Passwords do not match");
                return;
            }

            const payload = {
                email: data.email,
                username: data.username,
                first_name: data.firstname,
                last_name: data.lastname,
                role: data.role,
                phone_number: data.phone_number,
                password: data.password
            };

            try {
                const response = await fetch('/auth', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    window.location.href = '/auth/login-page';
                } else {
                    // Handle error
                    const errorData = await response.json();
                    alert(`Error: ${errorData.message}`);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            }
        });
    }





    // Helper function to get a cookie by name
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
    };

    function logout() {
        // Get all cookies
        const cookies = document.cookie.split(";");
    
        // Iterate through all cookies and delete each one
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i];
            const eqPos = cookie.indexOf("=");
            const name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
            // Set the cookie's expiry date to a past date to delete it
            document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/";
        }
    
        // Redirect to the login page
        window.location.href = '/auth/login-page';
    };