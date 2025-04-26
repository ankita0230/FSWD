const bulb = document.getElementById("bulb");
const onButton = document.getElementById("on-button");
const offButton = document.getElementById("off-button");

onButton.addEventListener("click", () => {
  bulb.src = "./assets/lightbulb-on.png";
});

offButton.addEventListener("click", () => {
  bulb.src = "./assets/lightbulb-off.png";
});
