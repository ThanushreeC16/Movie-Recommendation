import { useState } from "react";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import MovieDetails from "./pages/MovieDetails";
import "./styles/Home.css";
import "./styles/Login.css";
import "./styles/Register.css";
import "./styles/Dashboard.css";

function App() {
  const [page, setPage] = useState("home");
  const [user, setUser] = useState("");
  const [selectedMovie, setSelectedMovie] = useState(null);

  return (
    <div>
      {page === "home"      && <Home setPage={setPage} user={user} />}
      {page === "login"     && <Login setPage={setPage} setUser={setUser} />}
      {page === "register"  && <Register setPage={setPage} />}
      {page === "dashboard" && (
        <Dashboard
          setPage={setPage}
          setUser={setUser}
          user={user}
          setSelectedMovie={(movie) => { setSelectedMovie(movie); setPage("movie"); }}
        />
      )}
      {page === "movie" && selectedMovie && (
        <MovieDetails
          movie={selectedMovie}
          user={user}
          onBack={() => setPage("dashboard")}
          setPage={setPage}
          setUser={setUser}
          setSelectedMovie={(movie) => { setSelectedMovie(movie); setPage("movie"); }}
        />
      )}
    </div>
  );
}

export default App;
