container = document.getElementById("container");
let i = 0;

setInterval(refresh, 1000);

function refresh() {
  const date = new Date();
  container.innerHTML = `<h1>Date: ${date.getDate()} | ${
    date.getMonth() + 1
  } | ${date.getFullYear()}<h1>`;

  am_pm = date.getHours() < 12 ? "AM" : "PM";

  container.innerHTML += `<h1>Time: ${date.getHours()} : ${date.getMinutes()} : ${date.getSeconds()} ${am_pm}<h1>`;
}

function change() {
  var doc = document.getElementById("container");
  var color = ["grey", "blue", "brown", "green", "orange"];
  doc.style.backgroundColor = color[i];
  i = (i + 1) % color.length;
}

setInterval(change, 3000);
