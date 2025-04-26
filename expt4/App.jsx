import './App.css';
import Greeting from "./Greeting.jsx";
import {Counter} from "./Counter.jsx";
import TextInput from "./TextInput.jsx";

function App() {

  return (
    <div style={{ textAlign: "center", padding: "20px" }}>
      <Greeting name="Ved" />
      <Counter />
      <br />
      <TextInput />
    </div>
  )
}

export default App;