document
  .getElementById("registration-form")
  .addEventListener("submit", function (event) {
    event.preventDefault();
    let isValid = true;

    const name = document.getElementById("name").value.trim();
    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    const nameRegex = /^[A-Za-z\s]+$/;
    const usernameRegex = /^[a-zA-Z0-9_]{5,15}$/;
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$/;

    document.getElementById("name-error").textContent = nameRegex.test(name)
      ? ""
      : "Invalid name";
    document.getElementById("username-error").textContent = usernameRegex.test(
      username
    )
      ? ""
      : "Username should be 5-15 characters long and contain only letters, numbers, and underscores";
    document.getElementById("email-error").textContent = emailRegex.test(email)
      ? ""
      : "Invalid email format";
    document.getElementById("password-error").textContent = passwordRegex.test(
      password
    )
      ? ""
      : "Password must be at least 6 characters and contain at least one letter and one number";

    if (
      !nameRegex.test(name) ||
      !usernameRegex.test(username) ||
      !emailRegex.test(email) ||
      !passwordRegex.test(password)
    ) {
      isValid = false;
    }

    if (isValid) {
      alert("You have successfully submitted the form!");
      document.getElementById("registration-form").reset();
    }
  });
