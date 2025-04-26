let username = document.getElementById("username");
let email = document.getElementById("email");
let password = document.getElementById("password");
let confirmPassword = document.getElementById("confirmPassword");
let age = document.getElementById("age");
let country = document.getElementById("country");
let form = document.querySelector("form");

function validateName() {
    let pattern = /[A-z]{3,}$/;
    if(!pattern.test(username.value)) {
        return false;
    } else {
        return true;
    }
}

function validateEmail() {
    let pattern = /[A-z0-9._%+-]*@[A-z0-9.-]*\.[A-z]{2,}$/;
    if(!pattern.test(email.value)) {
        return false;
    } else {
        return true;
    }
}

function validatePassword() {
    let pattern = /[A-z0-9#@_]{8,}$/;
    if(!pattern.test(password.value)) {
        return false;
    } else {
        return true;
    }
}

function validateAge() {
    let pattern = /1[89]|[2-9][0-9]|100$/;
    if(!pattern.test(age.value)) {
        return false;
    } else {
        return true;
    }
}

function validateConfirmPassword() {
    if(!(password.value === confirmPassword.value)) {
        return false;
    } else {
        return true;
    }
}

username.addEventListener("change", () => {
    let namefb = document.getElementById("namefb");
    if(validateName()) {
        namefb.innerText = "Username looks Good!"
    } else {
        namefb.innerText = "Invalid Username!"
    }
});

email.addEventListener("change", () => {
    let emailfb = document.getElementById("emailfb");
    if(validateEmail()) {
        emailfb.innerText = "Email looks Good!"
    } else {
        emailfb.innerText = "Invalid Email!"
    }
});

password.addEventListener("change", () => {
    let passwordfb = document.getElementById("passwordfb");
    if(validatePassword()) {
        passwordfb.innerText = "Password looks Good!"
    } else {
        passwordfb.innerText = "Invalid Password!";
        if(password.value.length < 8) {
            let err = document.createElement("span");
            err.innerText = " Password should contain atleast 8 characters!";
            passwordfb.appendChild(err);
        }
    }
});

age.addEventListener("change", () => {
    let agefb = document.getElementById("agefb");
    if(validateAge()) {
        agefb.innerText = "Valid Age!"
    } else {
        agefb.innerText = "Age too Low!!"
    }
});

country.addEventListener("change", () => {
    let countryfb = document.getElementById("countryfb");
    if(country.value != "default") {
        countryfb.innerText = "Valid Country!"
    } else {
        countryfb.innerText = "Please select a Country!"
    }
});

confirmPassword.addEventListener("change", () => {
    let confirmPasswordfb = document.getElementById("confirmPasswordfb");
    if(validateConfirmPassword()) {
        confirmPasswordfb.innerText = "Correct Password!"
    } else {
        confirmPasswordfb.innerText = "Different Password!"
    }
});

form.addEventListener("submit", (event) => {
    if (validateAge() && validateName()  && validateEmail() && validatePassword() && validateConfirmPassword()){
        confirm("Hurray! Your account has been created!");
    } else {
        event.preventDefault();
        alert("Please re-validate your account details!");
    }
}); 