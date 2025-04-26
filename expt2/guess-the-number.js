const message = document.getElementById("message");

let username = prompt("Enter your name");

let random = Math.trunc(Math.random() * 100 + 1);
console.log(random);

let attempts;

for (attempts = 5; attempts > 0; attempts--) {
  let guess = +prompt(`${username} guess the number`);
  if (guess === random) {
    break;
  }
  if (attempts > 1) {
    if (guess < random) {
      alert(`Enter larger number (${attempts - 1} attempts remaining)`);
    } else {
      alert(`Enter smaller number (${attempts - 1} attempts remaining)`);
    }
  }
}

if (attempts === 0) {
  message.innerHTML = `${username}, You Lose`;
} else {
  message.innerHTML = `${username}, You Win`;
}
