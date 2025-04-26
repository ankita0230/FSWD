function addTodo() {
  let input = document.getElementById("todo-input");
  let task = input.value.trim();
  if (task === "") return;

  let li = document.createElement("li");
  li.innerHTML = `<span>${task}</span>
                  <button onclick="editTodo(this)">Edit</button>
                  <button onclick="deleteTodo(this)">Delete</button>`;

  document.getElementById("todo-list").appendChild(li);
  input.value = "";
}

function editTodo(button) {
  let li = button.parentElement;
  let newTask = prompt("Edit task:");
  if (newTask && newTask.trim() !== "") {
    let newLi = document.createElement("li");
    newLi.innerHTML = `<span>${newTask.trim()}</span>
                        <button onclick="editTodo(this)">Edit</button>
                        <button onclick="deleteTodo(this)">Delete</button>`;
    li.replaceWith(newLi);
  }
}

function deleteTodo(button) {
  let li = button.parentElement;
  li.remove();
}
